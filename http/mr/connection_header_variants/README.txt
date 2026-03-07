# Connection Header Variants - Metamorphic Relation

## Overview

This metamorphic relation tests the **transport-layer independence** of HTTP responses.

## The Relation

- **Input A**: HTTP request with `Connection: keep-alive` header
- **Input B**: HTTP request with `Connection: close` header (IDENTICAL request otherwise)
- **Expected Relation**: Both requests should receive identical response bodies and status codes

## RFC Reference

Per RFC 7230 (HTTP/1.1 Message Syntax and Routing):

> The "Connection" header field allows the sender to indicate desired control options for the current connection.

The Connection header is a **hop-by-hop** header that controls transport-layer behavior:
- `keep-alive`: Requests that the connection remain open for subsequent requests
- `close`: Signals that the connection will be closed after the response

**Key Insight**: The Connection header should only affect *how* the connection is managed, not *what* content is returned. The response body and status code must be identical regardless of the Connection header value.

## What This Tests

1. **Response Consistency**: Verifies the server returns the same content regardless of connection preferences
2. **Protocol Compliance**: Ensures the server correctly separates transport concerns from content delivery
3. **State Independence**: Confirms connection management doesn't leak into response generation

## Test Variants

The grammar generates test cases by varying (all enforced to be identical between A and B):

### HTTP Methods
- `GET`: Standard resource retrieval
- `HEAD`: Headers-only (tests no-body response handling)
- `OPTIONS`: Server capabilities (tests Allow header consistency)

### Paths
- `/`: Root path
- `/data`: Data endpoint
- `/api`: API endpoint
- `/api?param=value`: Path with single query parameter
- `/api?foo=bar&baz=123`: Path with multiple query parameters

### HTTP Versions
- `HTTP/1.1`: Modern standard
- `HTTP/1.0`: Legacy support (important: Connection header behavior differs)

### Headers
- **User-Agent**: Fandango/1.0, TestClient/2.0, Mozilla/5.0, curl/7.68.0
- **Accept**: */*, application/json, text/html, text/plain
- **Cache-Control**: (none), no-cache, max-age=0

### Theoretical Test Coverage
With equality constraints ensuring A and B are identical:
- 3 methods x 5 paths x 2 versions x 4 user-agents x 4 accept x 3 cache-control = 1,440 combinations

Fandango generates a representative subset through k-path coverage.

## Edge Cases Handled

### POST Requests
POST requests with bodies are intentionally **not included** in this MR because:
1. POST requests may trigger server-side state changes (e.g., database writes)
2. The same POST sent twice may result in different responses (e.g., duplicate key errors)
3. To properly test POST, you'd need idempotent endpoints or test isolation

If POST testing is desired, consider using:
- Idempotent endpoints (e.g., PUT or POST with unique identifiers)
- Test isolation with database rollbacks

### HTTP Version Differences
- In HTTP/1.0, connections default to `close` unless explicitly `keep-alive`
- In HTTP/1.1, connections default to `keep-alive` unless explicitly `close`
- The response content should be identical regardless of version

### Query Parameters
Query parameters are included to test:
- URL parsing consistency
- Query string handling doesn't interact with Connection header
- Cache behavior with query strings

### HEAD Method
The HEAD method returns only headers (no body). The validation handles this by:
- Comparing empty bodies correctly
- Ensuring status codes and Content-Type match

### OPTIONS Method
OPTIONS may return different headers (Allow), but core response should be consistent.

## Potential Violations

A violation would indicate:
- Server bug where connection state affects response content
- Improper caching behavior tied to connection type
- Resource handling differences based on connection lifecycle
- HTTP version-specific bugs in response generation

## Grammar Design

The grammar uses **equality constraints** to ensure A and B requests are identical:
```
where <method_A> == <method_B>
where <path_A> == <path_B>
where <http_version_A> == <http_version_B>
where <ua_A> == <ua_B>
where <accept_A> == <accept_B>
where <cache_control_A> == <cache_control_B>
```

This guarantees the only difference between requests is the Connection header value.

## Running the Test

```bash
# Start the HTTP servers first
node mt-http/http-server-3000.js &
node mt-http/http-server-3001.js &

# Run the metamorphic test
python mt-http/MRs/connection_header_variants/script.py
```

## Validation Logic

The `validateConnectionInvariance` function:
1. Extracts status codes from both responses
2. Extracts response bodies (handles chunked and non-chunked encoding)
3. Compares Content-Type headers (excluding Connection-related headers)
4. Reports PASS if all match, VIOLATION with details otherwise

## Known Limitations

1. Does not test POST/PUT/PATCH with request bodies
2. Does not test across different server implementations in the same run
3. Timing-sensitive responses (e.g., timestamps in body) may cause false positives
4. Large responses may be truncated in violation logging
