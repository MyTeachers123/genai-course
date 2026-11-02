# Capstone Pitch: Affordable Child Care Matching

**Problem.** Many low-income families in California are denied or wait-listed for subsidized or CalWORKs child care but still cannot afford market rates. Meanwhile, many licensed family child care homes have empty seats.

**What I will build.** A parent intake form and database for USCIC (uscic.us), a nonprofit. It collects only language, email, phone, ZIP code, monthly budget, and care schedule. Contact details are encrypted and used only by USCIC.

**How matching works.** USCIC sends an anonymous request (no name or contact) to MyTeachers123.com daycares in the same ZIP with open seats, asking if they would accept a lower price. If a daycare agrees, the parent gets a link to its MyTeachers123.com page and contacts the provider directly to book a visit.

**Model and architecture.** Parents can answer in their own language. Claude, through LangChain's ChatAnthropic with PydanticOutputParser, OutputFixingParser, and field validators, turns answers into validated records. Matching is rule-based. Stack: FastAPI, Postgres, LangChain.

**Course connection.** Extends Week 6 (prompt engineering, structured output, Pydantic validation). I will measure extraction accuracy, match rate, and cost per request.
