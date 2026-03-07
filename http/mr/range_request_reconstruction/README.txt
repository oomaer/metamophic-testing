# Range Request Reconstruction - Metamorphic Relation (MR4)

## Overview

This metamorphic relation tests that **partial content requests can be reconstructed** to equal the full resource, as specified in RFC 7233.

## The Relation

- **Input A**: Full GET request to `/large` (no Range header) → receives complete content
- **Input B**: Two partial GET requests with Range headers, concatenated:
  - First: `Range: bytes=0-499` → first 500 bytes
  - Second: `Range: bytes=500-` → remaining bytes
- **Expected Relation**: Concatenated response from B must exactly equal A's body

## RFC 7233 Specification

### Section 3.1 - Range Header
> *"The 'Range' header field on a GET request modifies the method semantics to request transfer of only one or more subranges of the selected representation data."*

### Section 2.1 - Byte Ranges
> Format: `bytes=0-499` for the first 500 bytes (offsets 0-499, inclusive).
>
> Open-ended range: `bytes=500-` means from byte 500 to end of content.

### Section 4.1 - 206 Partial Content
> *"The 206 (Partial Content) status code indicates that the server is successfully fulfilling a range request for the target resource by transferring one or more parts."*

### Content-Range Header
Response includes: `Content-Range: bytes 0-499/1234` indicating which bytes and total size.

## What This Tests

1. **Range Parsing Correctness**: Server correctly interprets byte range specifications
2. **Boundary Handling**: No off-by-one errors at range boundaries
3. **Content Integrity**: Partial responses contain exact bytes requested
4. **Reconstruction**: Multiple partial requests can rebuild the complete resource

## Test Variants

The grammar tests multiple split points:
- Split at byte 100 (early split)
- Split at byte 500 (middle split)
- Split at byte 800 (late split)
- Split at byte 200 and 600 (three-part reconstruction)

## Potential Violations

A violation would indicate:
- Off-by-one errors in range boundary calculation
- Content corruption during partial response generation
- Incorrect Content-Range header values
- Missing bytes at split boundaries
- Duplicate bytes at split points

## Running the Test

```bash
# Start the HTTP servers first
node mt-http/http-server-3000.js &
node mt-http/http-server-3001.js &

# Run the metamorphic test
python mt-http/MRs/range_request_reconstruction/script.py
```

## Server Requirements

The server must:
1. Support `Accept-Ranges: bytes` header
2. Parse `Range: bytes=X-Y` header correctly
3. Return 206 Partial Content with correct `Content-Range` header
4. Handle open-ended ranges (`bytes=500-`)
5. Return 416 Range Not Satisfiable for invalid ranges
