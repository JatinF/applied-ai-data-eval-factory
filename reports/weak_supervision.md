# Weak supervision

Backend: `local-probabilistic-v1`. Gold labels were not used to fit the model.

## v1

Coverage 1.0000, overlap 0.8667, conflict 0.3111.

| Labeling function | Coverage | Abstention | Estimated accuracy | Gold accuracy |
| --- | ---: | ---: | ---: | ---: |
| lf_password_reset | 0.1778 | 0.8222 | 0.7500 | 0.6667 |
| lf_error_401_403 | 0.1704 | 0.8296 | 0.6818 | 1.0000 |
| lf_database_timeout | 0.2370 | 0.7630 | 0.7544 | 0.7188 |
| lf_payments_service | 0.1704 | 0.8296 | 0.6522 | 0.6957 |
| lf_priority_incident | 0.1481 | 0.8519 | 0.9250 | 0.9500 |
| lf_runbook_match | 0.8148 | 0.1852 | 0.8768 | 0.9182 |
| lf_similar_case | 1.0000 | 0.0000 | 0.9182 | 0.8481 |
| lf_domain_dictionary | 0.6296 | 0.3704 | 0.8875 | 0.9176 |
| lf_repeated_failures | 0.1407 | 0.8593 | 0.9700 | 1.0000 |
| lf_network_terms | 0.2148 | 0.7852 | 0.6667 | 0.6897 |
| lf_timeout_to_network | 0.1778 | 0.8222 | 0.5100 | 0.0417 |
| lf_billing_keywords | 0.2296 | 0.7704 | 0.5100 | 0.5161 |
| lf_insufficient_evidence | 0.0000 | 1.0000 | 0.7000 | n/a |

## v2

Coverage 1.0000, overlap 0.8667, conflict 0.3111.

| Labeling function | Coverage | Abstention | Estimated accuracy | Gold accuracy |
| --- | ---: | ---: | ---: | ---: |
| lf_password_reset | 0.1778 | 0.8222 | 0.6977 | 0.6667 |
| lf_error_401_403 | 0.1704 | 0.8296 | 0.9700 | 1.0000 |
| lf_database_timeout | 0.2370 | 0.7630 | 0.7377 | 0.7188 |
| lf_payments_service | 0.1704 | 0.8296 | 0.6818 | 0.6957 |
| lf_priority_incident | 0.1481 | 0.8519 | 0.9487 | 0.9500 |
| lf_runbook_match | 0.8148 | 0.1852 | 0.9254 | 0.9182 |
| lf_similar_case | 1.0000 | 0.0000 | 0.9700 | 0.8481 |
| lf_domain_dictionary | 0.6296 | 0.3704 | 0.9000 | 0.9176 |
| lf_repeated_failures | 0.1407 | 0.8593 | 0.9700 | 1.0000 |
| lf_network_terms | 0.2148 | 0.7852 | 0.6809 | 0.6897 |
| lf_timeout_to_network | 0.1778 | 0.8222 | 0.5100 | 0.0417 |
| lf_billing_keywords | 0.2296 | 0.7704 | 0.5357 | 0.5161 |
| lf_insufficient_evidence | 0.0000 | 1.0000 | 0.7000 | n/a |
| lf_db_error_code | 0.1704 | 0.8296 | 0.9700 | 1.0000 |
| lf_pay_error_code | 0.1185 | 0.8815 | 0.9700 | 1.0000 |
| lf_auth_on_payments | 0.0519 | 0.9481 | 0.7000 | 1.0000 |
