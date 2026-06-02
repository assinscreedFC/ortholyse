---
phase: 1
slug: spike-clan
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-02
completed: 2026-06-02
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (+ pytest-cov 5.0) |
| **Config file** | `pyproject.toml [tool.pytest.ini_options]` (existing) |
| **Quick run command** | `pytest tests/test_clan_spike.py -q` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_clan_spike.py -q`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | SPIKE-01 | — | License verdict documented (BSD-3 CLAN + MOR FR grammar terms) | manual | n/a (license email/doc) | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | SPIKE-02 | — | `mor` runs headless on test `.cha`, produces `%mor` tier | manual | n/a (CLI trial captured) | ❌ W0 | ⬜ pending |
| 1-03-01 | 03 | 2 | SPIKE-03 | — | Python parser extracts `%mor` tokens | unit | `pytest tests/test_clan_spike.py::test_parse_mor_tier -q` | ❌ W0 | ⬜ pending |
| 1-03-02 | 03 | 2 | SPIKE-03 | — | Morpheme-MLU computed, plausible vs MTLN oracle | unit | `pytest tests/test_clan_spike.py::test_mlu_morphemes_vs_oracle -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_clan_spike.py` — unit tests for `%mor` parsing + morpheme-MLU (SPIKE-03)
- [ ] `tests/fixtures/` — reference `%mor` sample (snippet of MTLN `.cha` or fabricated `%mor` tier with known MLU)
- [ ] pytest already installed — no framework install needed

*Note: SPIKE-01 (license) and SPIKE-02 (`mor` CLI runs) are inherently manual/exploratory; only the SPIKE-03 parsing seed has automated coverage.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CLAN/TalkBank + MOR FR grammar redistribution license verdict | SPIKE-01 | License interpretation + external confirmation (email macw@cmu.edu for MOR FR grammar) | Document BSD-3 verdict for CLAN binary; obtain/cite explicit license for `fra.zip` MOR grammar; conclude Go/No-Go per D-07 |
| `mor` command runs headless on Windows on a test `.cha` and emits a readable `%mor` tier | SPIKE-02 | Requires the CLAN binary + grammar installed locally; one-time exploratory CLI run | Install CLANWin, run `mor` against a test `.cha` with FR grammar, capture stdout + resulting `%mor` tier |

*The reusable seed (subprocess wrapper + `%mor` parser, per D-05) IS automated-testable in Plan 03.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
