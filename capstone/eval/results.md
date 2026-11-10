# Capstone evaluation results

## Summary

| config              |   field_accuracy | records_fully_correct   |   privacy_violations |   match_rate |   avg_cost_per_request_usd |   cost_per_1000_requests_usd |
|:--------------------|-----------------:|:------------------------|---------------------:|-------------:|---------------------------:|-----------------------------:|
| rule-based baseline |            0.75  | 4/12                    |                    0 |        0.6   |                    0       |                         0    |
| GPT-4o              |            0.893 | 9/12                    |                    0 |        0.833 |                    0.00286 |                         2.86 |

## Correct answers per field (12 cases)

|                    |   rule-based baseline |   GPT-4o |
|:-------------------|----------------------:|---------:|
| language           |                     7 |       10 |
| zip_code           |                    10 |       11 |
| monthly_budget_usd |                     8 |       10 |
| age_groups         |                     5 |       11 |
| days               |                     9 |       11 |
| start              |                     9 |       11 |
| end                |                     8 |       11 |
| (cases)            |                    12 |       12 |

## rule-based baseline

|   id | result   |   correct_fields | all_correct   | privacy_ok   |   matches |   cost_usd | detail                                                                |
|-----:|:---------|-----------------:|:--------------|:-------------|----------:|-----------:|:----------------------------------------------------------------------|
|    1 | parsed   |                7 | True          | True         |         2 |          0 |                                                                       |
|    2 | parsed   |                7 | True          | True         |         2 |          0 |                                                                       |
|    3 | parsed   |                5 | False         | True         |         2 |          0 | language=English; age_groups=['toddler']                              |
|    4 | parsed   |                3 | False         | True         |         0 |          0 | monthly_budget_usd=600; age_groups=['infant']; start=08:00; end=17:00 |
|    5 | rejected |                0 | False         | True         |         0 |        nan | 'NoneType' object has no attribute 'group'                            |
|    6 | parsed   |                5 | False         | True         |         2 |          0 | language=English; age_groups=['toddler']                              |
|    7 | parsed   |                7 | True          | True         |         1 |          0 |                                                                       |
|    8 | parsed   |                5 | False         | True         |         0 |          0 | days=['Mon', 'Tue', 'Wed', 'Thu', 'Fri']; end=17:00                   |
|    9 | parsed   |                6 | False         | True         |         0 |          0 | age_groups=['infant', 'infant']                                       |
|   10 | parsed   |                6 | False         | True         |         0 |          0 | monthly_budget_usd=10                                                 |
|   11 | rejected |                7 | True          | True         |         0 |        nan | 1 validation error for CareNeed                                       |
|   12 | parsed   |                5 | False         | True         |         1 |          0 | language=English; age_groups=['toddler']                              |

## GPT-4o

|   id | result   |   correct_fields | all_correct   | privacy_ok   |   matches |   cost_usd | detail                                                                                                                   |
|-----:|:---------|-----------------:|:--------------|:-------------|----------:|-----------:|:-------------------------------------------------------------------------------------------------------------------------|
|    1 | parsed   |                7 | True          | True         |         2 |   0.002828 |                                                                                                                          |
|    2 | parsed   |                7 | True          | True         |         2 |   0.002843 |                                                                                                                          |
|    3 | parsed   |                7 | True          | True         |         1 |   0.002927 |                                                                                                                          |
|    4 | parsed   |                7 | True          | True         |         1 |   0.002932 |                                                                                                                          |
|    5 | parsed   |                7 | True          | True         |         1 |   0.00286  |                                                                                                                          |
|    6 | parsed   |                6 | False         | True         |         2 |   0.00288  | language=Filipino                                                                                                        |
|    7 | parsed   |                7 | True          | True         |         1 |   0.002873 |                                                                                                                          |
|    8 | parsed   |                7 | True          | True         |         0 |   0.002735 |                                                                                                                          |
|    9 | parsed   |                7 | True          | True         |         2 |   0.002837 |                                                                                                                          |
|   10 | parsed   |                6 | False         | True         |         1 |   0.00282  | monthly_budget_usd=866                                                                                                   |
|   11 | parsed   |                0 | False         | True         |         0 |   0.002933 | language=English; zip_code=90210; monthly_budget_usd=1000; age_groups=['toddler']; days=['Mon', 'Tue', 'Wed', 'Thu', 'Fr |
|   12 | parsed   |                7 | True          | True         |         1 |   0.002832 |                                                                                                                          |
