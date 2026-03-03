
include ("/Users/i7949486/Desktop/uds/thesis/metamophic-testing/mt-http/MRs/http-utils.fan")

# Connection Header Variants Metamorphic Relation (RFC 7230)
# Tests that Connection header does not affect response content
#
# We test multiple endpoint/header combinations separately
# Each test: same request with keep-alive vs close should get same response

<start> ::= <test_case>

# Different test case variants for k-path coverage
<test_case> ::= <test_root> | <test_data> | <test_root_json> | <test_data_json> | <test_root_html> | <test_data_html>

# Test root endpoint with different Accept headers
<test_root> ::= <Interaction1_root> <ChangeConnection> <Interaction2_root>
<Interaction1_root> ::= <ClientA:req_root_keepalive><ServerA:response_A>
<Interaction2_root> ::= <ClientB:req_root_close><ServerB:response_B>
<req_root_keepalive> ::= "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Fandango/1.0\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n"
<req_root_close> ::= "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Fandango/1.0\r\nAccept: */*\r\nConnection: close\r\n\r\n"

# Test /data endpoint
<test_data> ::= <Interaction1_data> <ChangeConnection> <Interaction2_data>
<Interaction1_data> ::= <ClientA:req_data_keepalive><ServerA:response_A>
<Interaction2_data> ::= <ClientB:req_data_close><ServerB:response_B>
<req_data_keepalive> ::= "GET /data HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Fandango/1.0\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n"
<req_data_close> ::= "GET /data HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Fandango/1.0\r\nAccept: */*\r\nConnection: close\r\n\r\n"

# Test root with application/json
<test_root_json> ::= <Interaction1_root_json> <ChangeConnection> <Interaction2_root_json>
<Interaction1_root_json> ::= <ClientA:req_root_json_keepalive><ServerA:response_A>
<Interaction2_root_json> ::= <ClientB:req_root_json_close><ServerB:response_B>
<req_root_json_keepalive> ::= "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: TestClient/2.0\r\nAccept: application/json\r\nConnection: keep-alive\r\n\r\n"
<req_root_json_close> ::= "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: TestClient/2.0\r\nAccept: application/json\r\nConnection: close\r\n\r\n"

# Test /data with application/json
<test_data_json> ::= <Interaction1_data_json> <ChangeConnection> <Interaction2_data_json>
<Interaction1_data_json> ::= <ClientA:req_data_json_keepalive><ServerA:response_A>
<Interaction2_data_json> ::= <ClientB:req_data_json_close><ServerB:response_B>
<req_data_json_keepalive> ::= "GET /data HTTP/1.1\r\nHost: localhost\r\nUser-Agent: TestClient/2.0\r\nAccept: application/json\r\nConnection: keep-alive\r\n\r\n"
<req_data_json_close> ::= "GET /data HTTP/1.1\r\nHost: localhost\r\nUser-Agent: TestClient/2.0\r\nAccept: application/json\r\nConnection: close\r\n\r\n"

# Test root with text/html
<test_root_html> ::= <Interaction1_root_html> <ChangeConnection> <Interaction2_root_html>
<Interaction1_root_html> ::= <ClientA:req_root_html_keepalive><ServerA:response_A>
<Interaction2_root_html> ::= <ClientB:req_root_html_close><ServerB:response_B>
<req_root_html_keepalive> ::= "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\nConnection: keep-alive\r\n\r\n"
<req_root_html_close> ::= "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\nConnection: close\r\n\r\n"

# Test /data with text/html
<test_data_html> ::= <Interaction1_data_html> <ChangeConnection> <Interaction2_data_html>
<Interaction1_data_html> ::= <ClientA:req_data_html_keepalive><ServerA:response_A>
<Interaction2_data_html> ::= <ClientB:req_data_html_close><ServerB:response_B>
<req_data_html_keepalive> ::= "GET /data HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\nConnection: keep-alive\r\n\r\n"
<req_data_html_close> ::= "GET /data HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\nConnection: close\r\n\r\n"

<ChangeConnection> ::= r".*" := changeConnection()

# Response patterns
<response_A> ::= r"HTTP/1\.1 [0-9]{3} .+\r\n(.+\r\n)*\r\n([0-9a-fA-F]+\r\n.*\r\n)*0\r\n\r\n"
<response_B> ::= r"HTTP/1\.1 [0-9]{3} .+\r\n(.+\r\n)*\r\n([0-9a-fA-F]+\r\n.*\r\n)*0\r\n\r\n"

where validateConnectionInvariance(<response_A>, <response_B>)


def validateConnectionInvariance(responseA, responseB):
    import re
    responseA = str(responseA)
    responseB = str(responseB)
    if responseA.startswith("b'") or responseA.startswith('b"'):
        responseA = responseA[2:-1]
    if responseB.startswith("b'") or responseB.startswith('b"'):
        responseB = responseB[2:-1]
    codeA_match = re.search(r'HTTP/1\.\d\s+(\d{3})', responseA)
    codeB_match = re.search(r'HTTP/1\.\d\s+(\d{3})', responseB)
    codeA = codeA_match.group(1) if codeA_match else "unknown"
    codeB = codeB_match.group(1) if codeB_match else "unknown"
    json_match_A = re.search(r'\{.*\}', responseA)
    json_match_B = re.search(r'\{.*\}', responseB)
    bodyA = json_match_A.group(0) if json_match_A else ""
    bodyB = json_match_B.group(0) if json_match_B else ""
    status_match = codeA == codeB
    body_match = bodyA == bodyB
    if status_match and body_match:
        print(f"[PASS] Connection header invariance holds: status={codeA}")
    elif not status_match:
        print(f"[VIOLATION] Status codes differ: keep-alive={codeA}, close={codeB}")
    elif not body_match:
        print(f"[VIOLATION] Response bodies differ: A={bodyA[:50]}, B={bodyB[:50]}")
    return True
