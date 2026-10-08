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
| [#45](https://github.com/mwilsoniii23/pytest-api-framework/issues/45) | 3-Medium | Design        | `POST /auth`           | Invalid data returns 200 "Bad Credentials" response                                | `tests/functional/test_auth.py::test_auth_with_invalid_credentials_is_rejected`         |
| [#46](https://github.com/mwilsoniii23/pytest-api-framework/issues/46) | 3-Medium | Design        | `POST /auth`           | No Payload in request returns 200 "Bad Credentials" response                       | `tests/functional/test_auth.py::test_auth_without_payload_is_rejected`                  |
| [#47](https://github.com/mwilsoniii23/pytest-api-framework/issues/47) | 5-Minor  | Design        | `GET /ping`            | Unsupported method TRACE returned 404, expected 405 Method Not Allowed             | `tests/functional/test_booking_health.py::test_unsupported_method_trace_returns_405`    |
| [#48](https://github.com/mwilsoniii23/pytest-api-framework/issues/48) | 2-High   | Design        | `GET /booking`         | An empty `checkout` query parameter crashes the server                             | `tests/functional/test_booking_get_all_bookings_with_empty_checkout_query_parameter.py` |
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

**Impact:** A developer implementing partial updates from the documented spec gets 403 with no stated cause. The failure gives no indication that authentication is the issue, so the likely debugging path is the payload format rather than auth.

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

## 42 – `additionalneeds` is documented as required (`"optional": false`) on CreateBooking

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
-d '{"firstname":"James"}'
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

## 45 – Invalid data returns 200 "Bad Credentials" response 

**Severity:** 3-Medium \
**Type:** Design \
**Endpoint:** `POST /auth`

**Repro**

```bash
curl --location 'https://restful-booker.herokuapp.com/auth' \
--header 'Content-Type: application/json' \
--data '{
    "username": "",
    "password": ""
}'
```

**Expected:** 

Invalid data should have been rejected \
Expected: 400, 401, 403, 404, 405, 406, 409, 415, 422, 428, 429, 5xx

**Actual:** 

API accepted the schema-violating request and returned 200 "Bad Credentials" response

[200] OK:
```json
{"reason": "Bad credentials"}
```

**Impact:** 



**Covered by:**

`tests/functional/test_auth.py::test_auth_with_invalid_credentials_is_rejected` 

---

## 46 – No Payload in request returns 200 "Bad Credentials" response 

**Severity:** 3-Medium \
**Type:** Design \
**Endpoint:** `POST /auth`

**Repro**

```bash
curl --location --request POST 'https://restful-booker.herokuapp.com/auth' \
--header 'Content-Type: application/json'
```

**Expected:** 

Invalid data should have been rejected \
Expected: 400, 401, 403, 404, 405, 406, 409, 415, 422, 428, 429, 5xx

**Actual:** 

API accepted the schema-violating request and returned 200 "Bad Credentials" response

[200] OK:
```json
{"reason": "Bad credentials"}
```

**Impact:** 



**Covered by:**

`tests/functional/test_auth.py::test_auth_without_payload_is_rejected`

---

## 47 – Unsupported method TRACE returned 404, expected 405 Method Not Allowed 

**Severity:** 5-Minor \
**Type:** Design \
**Endpoint:** `GET /ping`

**Repro**

```bash
curl -X TRACE https://restful-booker.herokuapp.com/ping
```

**Expected:** 

expected 405 Method Not Allowed \
Return 405 for methods not listed in the OpenAPI spec

**Actual:** 

Unsupported method TRACE returned 404

[404] Not Found:
    `Not Found`

**Impact:** 



**Covered by:**

`tests/functional/test_booking_health.py::test_unsupported_method_trace_returns_405`

---

## 48 – An empty `checkout` query parameter crashes the server

**Severity:** 2-High \
**Type:** Design \
**Endpoint:** `GET /booking?checkout=`

**Repro**

```bash
curl -X GET 'https://restful-booker.herokuapp.com/booking?checkout='
```

**Expected:** 

Expected `400 - Bad Request`

**Actual:** 

`500 - Internal Server Error`

**Impact:** 



**Covered by:**

`tests/functional/test_booking_get_all_bookings_with_empty_checkout_query_parameter.py`

---
