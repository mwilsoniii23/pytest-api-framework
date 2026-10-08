# Defects Found in the System Under Test

Restful Booker (https://restful-booker.herokuapp.com), a public demo API.
Each entry links to the covering regression test.

| #                                                                     | Severity | Type          | Endpoint               | Summary                                                                            | Test                                                                                    |
|-----------------------------------------------------------------------|----------|---------------|------------------------|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| [#16](https://github.com/mwilsoniii23/pytest-api-framework/issues/16) | 3-Medium | Documentation | `PATCH /booking/{id}`  | Requires an auth token, but the `/auth` documentation lists only PUT and DELETE    | `tests/functional/test_booking_patch.py::test_patch_without_auth_token_is_rejected`     |
| [#40](https://github.com/mwilsoniii23/pytest-api-framework/issues/40) | 3-Medium | Design        | `DELETE /booking/{id}` | DELETE returns `201 Created`                                                       | `tests/functional/test_booking_delete.py::test_delete_booking_returns_success_status`   |
| [#41](https://github.com/mwilsoniii23/pytest-api-framework/issues/41) | 4-Low    | Design        | `GET /ping`            | `/ping` returns `201 Created`                                                      | `tests/functional/test_booking_health.py::test_health_check_returns_200`                |
| [#42](https://github.com/mwilsoniii23/pytest-api-framework/issues/42) | 3-Medium | Documentation | `POST /booking/`       | `additionalneeds` is documented as required (`"optional": false`) on CreateBooking | `tests/functional/test_create_booking.py::test_create_booking_requires_additionalneeds` |
| [#43](https://github.com/mwilsoniii23/pytest-api-framework/issues/43) | 5-Minor  | Documentation | `PATCH /booking/{id}`  | The PATCH documentation examples all use `curl -X PUT`                             | Not Automatable - documentation only                                                    |
---

## #16 — PATCH requires auth, undocumented

**Severity:** 3-Medium \
**Type:** Documentation defect — behavior is reasonable, the docs are wrong \
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

**Covered by:** `tests/functional/test_booking_patch.py::test_patch_without_auth_token_is_rejected`

---

## 40 – DELETE returns 201 Created

**Severity:** 3-Medium \
**Type:** Design \
**Endpoint:** `DELETE /booking/{id}`

**Repro**
```bash
curl -i -X DELETE https://restful-booker.herokuapp.com/booking/910 \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

**Expected:** 

A successful `DELETE` response should return one of the standard success statuses for deletion:

- `200 OK` - deletion completed and a response body is returned
- `202 Accepted` - deletion request accepted for processing
- `204 No Content` - deletion completed and no response body is returned

Returning `201 Created` is semantically incorrect because the `DELETE` method does not create a resource.

**Actual:** 

The API returns:
`http HTTP/1.1 201 Created`

**Impact:**

Clients may interpret `201 Created` as meaning a new resource was created, which is misleading for a delete operation. 
This can cause incorrect client behavior, inaccurate logs/metrics, and confusion when validating the API against HTTP 
semantics or an OpenAPI contract.

**Covered by:** `tests/functional/test_booking_delete.py::test_delete_booking_returns_success_status`

---

## 41 – `/ping` returns `201 Created`

**Severity:** 4-Low \
**Type:** Design \
**Endpoint:** `GET /ping`

**Repro**
```bash
curl --location https://restful-booker.herokuapp.com/ping
```

**Expected:** 
`HTTP/1.1 200 OK`

**Actual:** 
`HTTP/1.1 201 Created`

**Impact:** 



**Covered by:** `tests/functional/test_booking_health.py::test_health_check_returns_200`

---

## 42 – `additionalneeds` is documented as required ('"optional": false') on CreateBooking

**Severity:** 3-Medium \
**Type:** Documentation \
**Endpoint:** `POST /booking`

**Repro**
```bash
curl --location 'https://restful-booker.herokuapp.com/booking' \
--header 'Content-Type: application/json' \
--data '{
    "firstname": "Jim",
    "lastname": "Brown",
    "totalprice": 111,
    "depositpaid": true,
    "bookingdates": {
        "checkin": "2018-01-01",
        "checkout": "2019-01-01"
    }
}'
```

**Expected:** 

`400 Bad Request`
If additionalneeds is required, booking app should reject the request

**Actual:** 

`200 OK`

**Impact:** 

**Covered by:** `tests/functional/test_create_booking.py::test_create_booking_requires_additionalneeds`

---

## 43 – The PATCH documentation examples all use `curl -X PUT`

**Severity:** 5-Minor \
**Type:** Documentation \
**Endpoint:** `PATCH /booking/{id}`

**Repro**

Review the public API documentation for `PATCH /booking/{id}` and inspect the example `curl` commands.

The examples are listed under the PATCH endpoint, but the commands use `PUT`:
```bash
curl -X PUT https://restful-booker.herokuapp.com/booking/<booking_id>
```

**Expected:** 

The `PATCH /booking/{id}` documentation should show examples using the PATCH method:
```bash
curl -X PATCH https://restful-booker.herokuapp.com/booking/<booking_id> \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-H "Cookie: token=<auth_token>" \
-d '{"fistname":"James"}'
```
**Actual:** 

The examples under the PATCH endpoint use `curl -X PUT`, which documents a full update request instead of a partial 
update request.

**Impact:** 

Minor documentation defect. Users can still infer the correct endpoint from the section title, but copying the example 
as-is sends a `PUT` request instead of a `PATCH` request. That can lead to accidental full-update behavior, failed 
requests if the payload is partial, or confusion while debugging PATCH behavior.

**Covered by:**

Documentation-only defect; no automated test coverage.

---