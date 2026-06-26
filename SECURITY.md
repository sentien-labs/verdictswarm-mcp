# Security Policy

## Supported Versions

Security fixes target the default branch until the project defines a version support policy.

## Reporting A Vulnerability

Please do not open public issues for leaked API keys, payment verification bugs, private reports, wallet/customer data exposure, or vulnerabilities.

Use GitHub private vulnerability reporting if it is enabled for this repository. If it is not enabled, contact the repository owner and include:

- a short description of the issue;
- steps to reproduce it;
- whether API keys, payment state, scan reports, wallet data, or user data are affected;
- suggested remediation, if known.

## Data Safety Notes

Do not commit `.env` files, `VS_API_KEY`, private reports, local logs containing private data, or customer/wallet research. Tests should use mocks, fixtures, or public sample token addresses.
