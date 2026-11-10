# Week 7 Homework: 20-Question Evaluation Table

GPT-4o + FAISS (all-MiniLM-L6-v2, 800-character chunks, k=4) over 10 Wikipedia articles on US/California family-support programs.
Scores 1-5 are from a GPT-4o judge with a rubric (retrieval, answer quality) and the faithfulness gate; I reviewed every row.
Rows marked * were changed or annotated after review (see `failure_audit.md`).

| # | Category | Question | Retrieval 1-5 | Answer 1-5 | Faithfulness 1-5 | Correct | Format OK | Answer (shortened) |
|---|---|---|---|---|---|---|---|---|
| 1 | positive | What does the name CalWORKs stand for? | 5 | 5 | 5 | yes | yes | CalWORKs stands for the California Work Opportunities and Responsibility to Kids program. Source: CalWORKs |
| 2 | positive | In what year did the Head Start program begin? | 5 | 5 | 5 | yes | yes | The Head Start program began in 1965. Source: Head Start (program). |
| 3 | positive | Which earlier program did TANF replace? | 5 | 5 | 5 | yes | yes | TANF replaced the Aid to Families with Dependent Children (AFDC) program. Source: [Temporary Assistance for Needy Families], [Aid to Families with Dep... |
| 4 | positive | Which president signed the Personal Responsibility and Work Opportunity Act? | 5 | 5 | 5 | yes | yes | President Bill Clinton signed the Personal Responsibility and Work Opportunity Reconciliation Act of 1996 into law. Source: Personal Responsibility an... |
| 5 | positive | What was SNAP called before it was renamed? | 5 | 5 | 5 | yes | yes | SNAP was formerly and colloquially known as the Food Stamp Program, or simply food stamps. Source: Supplemental Nutrition Assistance Program |
| 6* | positive | What is Medi-Cal? | 1 | 1 | 5 | no* | yes | Not found in the knowledge base.   Source: CalWORKs |
| 7* | positive | Who can receive WIC benefits? | 5 | 5 | 5 | partial* | yes* (checker split "U.S.") | WIC benefits are part of the U.S. Special Supplemental Nutrition Program for Women, Infants, and Children. This program is designed to support women, ... |
| 8 | positive | In what year was the Child Care and Development Block Grant created? | 5 | 5 | 5 | yes | yes | The Child Care and Development Block Grant was first authorized under the CCDBG Act of 1990. Source: Child Care and Development Block Grant. |
| 9 | positive | What age group does Early Head Start serve? | 5 | 5 | 5 | yes | yes | Early Head Start serves infants and toddlers, beginning as early as birth, and promotes healthy prenatal outcomes and healthy families. Source: Head S... |
| 10 | positive | Is the earned income tax credit refundable? | 5 | 5 | 5 | yes | yes | Yes, the earned income tax credit is refundable. This means that if the credit exceeds the amount of taxes owed, the taxpayer can receive the differen... |
| 11 | negative | What is the monthly tuition for infant care at family child care homes in ZIP code 91770? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: Child Care and Development Block Grant, Child and Dependent Care Credit. |
| 12 | negative | How many licensed family child care homes are there in Rosemead, California? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: [CalWORKs], [Personal Responsibility and Work Opportunity Reconciliation Act of 1996], [Head Start (program... |
| 13 | negative | What is the phone number of the USCIC parent help line? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: [CalWORKs], [Head Start (program)], [Child Care and Development Block Grant] |
| 14 | negative | Which daycare in El Monte has an infant opening this month? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: Head Start (program), Child Care and Development Block Grant |
| 15 | negative | What documents does the Los Angeles County office ask for at a CalWORKs appointment in 2026? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: CalWORKs |
| 16 | adversarial | Why was Head Start shut down by the 1996 welfare reform law? | 5 | 5 | 5 | yes | yes | The question contains a false assumption. The 1996 welfare reform law, known as the Personal Responsibility and Work Opportunity Reconciliation Act, d... |
| 17 | adversarial | CalWORKs is run by the US Department of Agriculture, so which USDA office handles CalWORKs appeals? | 5 | 5 | 5 | yes | yes | False assumption: CalWORKs is not run by the US Department of Agriculture. It is managed by the California Department of Social Services (CDSS) and ad... |
| 18 | adversarial | What is the exact federal minimum wage that TANF work requirements use? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: Temporary Assistance for Needy Families |
| 19 | adversarial | According to these documents, what percentage of eligible children did CCDBG serve in 2025? | 5 | 5 | 5 | yes | yes | Not found in the knowledge base.   Source: Child Care and Development Block Grant |
| 20 | adversarial | WIC is only for women, so babies cannot get WIC, right? | 5 | 5 | 5 | yes | yes | False assumption. The WIC program is the U.S. Special Supplemental Nutrition Program for Women, Infants, and Children, which means it is designed to s... |

**Totals:** positive 9/10 correct as judged (8 correct + 1 partial after review), negative 5/5, adversarial 5/5; overall 19/20 by the judge, 18/20 fully correct after review.
