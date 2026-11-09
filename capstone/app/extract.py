"""Turn a parent's free-text answer (any language) into a validated CareNeed record.

Claude via LangChain ChatAnthropic -> PydanticOutputParser -> OutputFixingParser (one repair call)
-> Pydantic field validators. Set CAPSTONE_LLM=openai to use GPT instead, or mock for offline tests.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .schemas import CareNeed

PRICES = {  # USD per 1M tokens (input, output)
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "gpt-4o": (2.50, 10.00),
}

SYSTEM = """You help a nonprofit that matches families with affordable licensed child care in California.
Read the parent's answer (it may be in any language) and fill the record.
Rules:
- Do not copy names, email addresses or phone numbers into any field.
- monthly_budget_usd is the total per month; convert weekly amounts with x4.33 and hourly with hours per month.
- age_groups: infant = under 24 months, toddler = 2 to 5 years, school_age = 6 years or older. One entry per child.
- Times are 24h HH:MM. "mornings" = 08:00-12:00, "full day" = 08:00-17:00 if no times are given.
- Write notes in English.
{format_instructions}"""

parser = PydanticOutputParser(pydantic_object=CareNeed)
prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", "Parent answer:\n{answer}")]).partial(
    format_instructions=parser.get_format_instructions())


@dataclass
class ExtractResult:
    need: CareNeed
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_s: float
    repaired: bool


def _llm():
    backend = os.environ.get("CAPSTONE_LLM", "claude")
    if backend == "openai":
        from langchain_openai import ChatOpenAI
        name = os.environ.get("CAPSTONE_MODEL", "gpt-4o")
        return ChatOpenAI(model=name, temperature=0), name
    from langchain_anthropic import ChatAnthropic
    name = os.environ.get("CAPSTONE_MODEL", "claude-sonnet-4-5")
    return ChatAnthropic(model=name, temperature=0, max_tokens=800), name


def extract(answer: str) -> ExtractResult:
    if os.environ.get("CAPSTONE_LLM") == "mock":
        return _mock_extract(answer)
    llm, name = _llm()
    t0 = time.time()
    msg = (prompt | llm).invoke({"answer": answer})
    usage = getattr(msg, "usage_metadata", None) or {}
    tin, tout = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
    repaired = False
    try:
        need = parser.parse(msg.content)
    except OutputParserException:
        from langchain_classic.output_parsers import OutputFixingParser
        need = OutputFixingParser.from_llm(parser=parser, llm=llm).parse(msg.content)
        repaired = True
    pin, pout = PRICES.get(name, (0, 0))
    return ExtractResult(need, name, tin, tout, round(tin / 1e6 * pin + tout / 1e6 * pout, 6),
                         round(time.time() - t0, 2), repaired)


def _mock_extract(answer: str) -> ExtractResult:
    """Deterministic rule-based parser for tests (English/Spanish keywords only)."""
    a = answer.lower()
    zip_code = re.search(r"(?<!\d)\d{5}(?!\d)", a).group(0)
    budget = int(re.search(r"\$\s?(\d[\d,]*)", a).group(1).replace(",", ""))
    groups = []
    groups += ["infant"] * len(re.findall(r"\b(\d+)[- ]?(?:month|mes)", a))
    groups += ["toddler"] * len([y for y in re.findall(r"\b(\d+)[- ]?(?:year|a\w?o)", a) if 2 <= int(y) <= 5])
    groups += ["school_age"] * len([y for y in re.findall(r"\b(\d+)[- ]?(?:year|a\w?o)", a) if int(y) >= 6])
    times = re.findall(r"\b(\d{1,2}):(\d{2})\b", a)
    start, end = ("08:00", "17:00") if len(times) < 2 else (f"{int(times[0][0]):02d}:{times[0][1]}", f"{int(times[1][0]):02d}:{times[1][1]}")
    language = "Spanish" if any(w in a for w in ("hijo", "hija", "necesito", "mes")) else "English"
    need = CareNeed(language=language, zip_code=zip_code, monthly_budget_usd=budget, age_groups=groups or ["toddler"],
                    schedule={"days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "start": start, "end": end})
    return ExtractResult(need, "mock", 0, 0, 0.0, 0.0, False)
