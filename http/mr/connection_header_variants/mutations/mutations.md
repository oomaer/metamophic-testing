# Mutation Testing for Connection Header Variants MR

## Metamorphic Relation
**Connection header should not affect response content**
- Request A: `Connection: keep-alive`
- Request B: `Connection: close`
- Expected: Same status code and response body

## Mutations Applied (5 total)

| ID  | Name | Description | Expected Detection |
|-----|------|-------------|-------------------|
| M1  | Different status for close | Return 201 instead of 200 when `Connection: close` | YES |
| M2  | Error on close | Return 500 when `Connection: close` | YES |
| M3  | Return 204 No Content | Return 204 with empty body for close | YES |
| M8  | Empty body | Return 200 but with empty body | YES |
| M20 | Different transfer encoding | Use chunked encoding for close requests | NO |

## Mutation Categories

### Detectable Mutations (M1, M2, M3, M8)
These mutations change the HTTP status code or response body for `Connection: close` requests.
The MR validates status code and body equality, so these should be detected.

### Undetectable Mutations (M20)
M20 should NOT be detected because the MR only compares body content, not transfer encoding.
The decoded body is identical regardless of whether Content-Length or chunked encoding is used.

## Usage

Run mutant server with specific mutation:
```bash
MUTATION=M1 node mutant-server-3001.js
```

Run all mutations:
```bash
python run_mutations.py
```

## Files
- `mutant-server-3001.js` - Server with all mutations (flag-controlled)
- `mutations.md` - This file (mutation documentation)
- `run_mutations.py` - Script to run all mutations and collect results
- `mutation_results.txt` - Results of mutation testing
- `log_*.txt` - Individual log files for each mutation run
