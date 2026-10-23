# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

We take the security of this repository, our data pipelines, and the offline study tools seriously.

If you discover a security vulnerability, please report it privately:
1. **Do not open a public GitHub issue.**
2. Send an email with details, proof-of-concept, and impact assessment to:  
   **`emilsyszanella@gmail.com`**
3. Include:
   - Type of issue (e.g., Cross-Site Scripting, dependency vulnerability, logic flaw).
   - Steps to reproduce.
   - Affected files and components.

You will receive an acknowledgment within 48 hours and an advisory once a patch has been published.

## Repository Security Protections

This repository enforces:
- **Branch Protection**: Direct deletion and force pushes (`git push --force`) are blocked on the `main` branch.
- **Secret Scanning & Push Protection**: Automated scanning blocks commits containing tokens, private keys, or API credentials.
- **Dependabot Security Alerts**: Automatic dependency vulnerability audits and security patches.
- **Access Control**: Only authorized maintainers have direct write access. External contributions require review via Pull Request forks.
