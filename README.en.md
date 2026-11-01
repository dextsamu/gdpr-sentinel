# gdpr-sentinel

**A technical and documentary GDPR / ePrivacy review skill for AI coding agents. It maps real processing, finds gaps with evidence, and never declares compliance.**
Built for Claude; the sister skill [`appsec-sentinel`](https://github.com/dextsamu/appsec-sentinel) covers application security. Apache-2.0. © Samuele Cucurnia and Pietro Previtali.

> **Commands and language.** Every command works in English or Italian (`quick`/`rapido`, `refute`/`smentita`, `close`/`chiudi`…): see the [command card](docs/COMMAND-CARD.md). The skill writes chat, findings and reports in the language you use. Machine-readable files keep canonical Italian field names and enum values because the scripts check them. The PDF generator produces an English report with `--lang en`.
>
> **Language note.** The skill's own instructions, references and templates are written in Italian (Italian public bodies and associations); the agent applies them and answers in your language. This page is a short English guide.

## What it does

- Builds a **map of the processing that actually happens** (data, purposes, roles, legal basis, recipients, transfers, retention) from code, schema, configuration and documents, and compares it with the privacy notice and cookie banner.
- Reviews **controls A–N** (lawfulness, notice, rights, retention, suppliers and transfers, security, breach, DPIA, cookies/tracking, and more). Finding states: *found*, *confirmed from code/config*, *hypothesis*, *not verifiable*. It never writes "compliant".
- **Refutation pass:** every gap marked found or confirmed is challenged by someone other than its author (`outcome | verifier | attempts`); self-refutation is not valid.
- No personal data or secret values in any output, including chat.

## Scripts (standard library; Playwright only for the cookie scan)

`cookie_scan.py` (clean browser, before consent, cookie names never values), `draft_ropa.py` (draft Art. 30 register and suppliers from code), `draft_dpia.py` (draft Art. 35 sheets with indicators to discuss; not a DPIA), `retention_check.py`, `check_matrix.py`, `redact_check.py`, `compare_audits.py`, `check_delivery.py`, `build_report_pdf.py`. Template for handling data-subject requests: `assets/richiesta-interessato-template.md` (Italian, to be reviewed by legal counsel before use).

## Install

Same as appsec-sentinel: `.skill` upload in Claude.ai, folder copy for Claude Code, `SKILL.md` convention for Codex CLI and Antigravity (see [`docs/ALTRI-AGENTI.md`](docs/ALTRI-AGENTI.md)), or `npx skills add <owner>/gdpr-sentinel` (discovery checked on a local path).

## Limits

Not legal advice and not a DPO. It shows what the software can process and send, not who is controller or processor, nor legal bases or countries: those stay "to verify with the controller". The cookie scan was validated on a local lab page; domain classification is indicative. Cross-agent testing is a single run per agent.

## Tests

`python3 tests/run_checks.py` (30 at the time of writing).
