# Defects Found in the System Under Test

Restful Booker (https://restful-booker.herokuapp.com), a public demo API.
Each entry links to the covering regression test.

| # | Severity | Endpoint | Summary | Test |
|---|---|---|---|---|
| [#3](link) | Major | `PATCH /booking/{id}` | Partial update returns 200 without persisting | `tests/negative/test_patch.py::test_partial_update_persists` |

---

## #3 — PATCH returns 200 without persisting

**Severity:** Major
**Endpoint:** `PATCH /booking/{id}`

**Repro**
```bash
    curl -X PATCH ... 
```

**Expected:** 200 with the updated resource; subsequent GET reflects the change.
**Actual:** 200 returned, subsequent GET shows original values.
**Impact:** A client has no way to distinguish a successful update from a silent no-op.
**Covered by:** `tests/negative/test_patch.py::test_partial_update_persists`