# Quality gate

Release target: at least 95/100 with observable evidence.

| Dimension | Weight | Evidence | Score |
|---|---:|---|---:|
| Cross-agent interoperability | 20 | Open Agent Skills layout; tested links for both hosts | 20 |
| Safe installation and recovery | 20 | Dry-run, idempotence, conflict refusal, owned-link uninstall | 20 |
| Privacy and supply-chain safety | 20 | Public hook, repository scan, full source pins, license gate | 19 |
| Reproducibility | 20 | Catalog profiles, standard-library CLI, fast-forward bootstrap, CI | 19 |
| Maintenance and usability | 20 | Doctor, status, upstream drift, update ledger, concise runbook | 19 |
| **Total** | **100** |  | **97** |

The score intentionally leaves three points open:

- regex scanning cannot prove the absence of every secret;
- configuration examples still require a deliberate merge into existing local
  settings;
- native Windows bootstrap has not been implemented.

The score is valid only while the automated tests, strict doctor, and public
repository checks pass.
