# Defects Found in the System Under Test

Restful Booker (https://restful-booker.herokuapp.com), a public demo API.
Each entry links to the covering regression test.

| #                                                                     | Severity | Type          | Endpoint              | Summary                                                                         | Test                                                                     |
|-----------------------------------------------------------------------|----------|---------------|-----------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| [#16](https://github.com/mwilsoniii23/pytest-api-framework/issues/16) | 3-Medium | Documentation | `PATCH /booking/{id}` | Requires an auth token, but the `/auth` documentation lists only PUT and DELETE | `tests/functional/test_booking_patch.py::test_patch_requires_auth_token` |

---

## #16 — PATCH requires auth, undocumented

**Severity:** 3-Medium
**Type:** Documentation defect — behavior is reasonable, the docs are wrong
**Endpoint:** `PATCH /booking/{id}`

**Repro**
```bash
curl -i -X PATCH https://restful-booker.herokuapp.com/booking/910 \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "firstname":"James",
    "lastname":"Brown"
    }'
```

**Expected:** Success. The `/auth` documentation states the token is "to use for access to the PUT and DELETE /booking" — PATCH is not listed, implying no token is required.

**Actual:** `403 Forbidden`. The same request with `Cookie: token=<token>` succeeds.

**Impact:** A developer implementing partial updates from the documented spec gets 403s with no stated cause. The failure gives no indication that authentication is the issue, so the likely debugging path is payload format rather than auth.

**Covered by:** `tests/functional/test_booking_patch.py::test_patch_requires_auth_token`