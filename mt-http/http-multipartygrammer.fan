from typing import Optional
import random
class ClientA(NetworkParty):
    def __init__(self):
        super().__init__(
            connection_mode=ConnectionMode.CONNECT,
            uri=f"tcp://localhost:{3000}"
        )
        self.start()

    def receive(self, message: str | bytes, sender: Optional[str]) -> None:
        super().receive(message, "ServerA")

class ServerA(NetworkParty):
    def __init__(self):
        super().__init__(
            connection_mode=ConnectionMode.EXTERNAL,
            uri=f"tcp://localhost:{3000}"
        )
        self.start()

    def receive(self, message: str | bytes, sender: Optional[str]) -> None:
        super().receive(message, "ClientA")

class ClientB(NetworkParty):
    def __init__(self):
        super().__init__(
            connection_mode=ConnectionMode.CONNECT,
            uri=f"tcp://localhost:{3001}"
        )
        self.start()

    def receive(self, message: str | bytes, sender: Optional[str]) -> None:
        super().receive(message, "ServerB")

class ServerB(NetworkParty):
    def __init__(self):
        super().__init__(
            connection_mode=ConnectionMode.EXTERNAL,
            uri=f"tcp://localhost:{3001}"
        )
        self.start()

    def receive(self, message: str | bytes, sender: Optional[str]) -> None:
        super().receive(message, "ClientB")


def get_random_header_order() -> str:
    headers = [
        "Host: localhost\r\n",
        "User-Agent: Fandango/1.0\r\n",
        "Accept: */*\r\n"
    ]
    random.shuffle(headers)
    return ''.join(headers)

#!grammer
<start> ::= <ClientA:ServerA:get_request_A> <ServerA:ClientA:response1> <ClientB:ServerB:get_request_B> <ServerB:ClientB:response2>

<get_request_A> ::= "GET / HTTP/1.1" <line_end> <headers_order_1> <line_end>
<get_request_B> ::= "GET / HTTP/1.1" <line_end> <headers_order_2> <line_end>

<line_end> ::= "\r\n"

<headers_order_1> ::= ->header_order_1
<headers_order_2> ::= ->header_order_2
# <headers_order_1> ::= <headers> := get_random_header_order()
# <headers_order_2> ::= <headers> := get_random_header_order()
# <headers> ::= r"([\w-]+: .*\r\n)*"


<response2> ::= <status_line> <headers_resp> "\r\n" <chunked_body>
<response1> ::= <status_line> <headers_resp> "\r\n" <chunked_body>
<status_line> ::= "HTTP/1.1 200 OK\r\n"

<headers_resp> ::= r"([\w-]+: .*\r\n)*" := "Content-Type: application/json\r\n"

<chunked_body> ::= <chunk_size> <json_data> <terminator>
<chunk_size> ::= r"[0-9a-fA-F]+\r\n" := "22\r\n"
<json_data> ::= r"\{.*\}\r\n" := '{"message":"Success","status":200}\r\n'
<terminator> ::= "0\r\n\r\n"

where <headers_order_1> != <headers_order_2>
where is_equivalent(<response1>, <response2>) == True

def is_equivalent(resp1: DerivationTree, resp2: DerivationTree) -> bool:
    return resp1.to_string().strip() == resp2.to_string().strip()
