import random
import uuid

from typing import Optional


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


uuid = str(uuid.uuid4())

def get_mutation(order):
    # print("order", order.to_string())
    hash_id = hash(order.to_string() + uuid)
    headers = [h.strip() for h in order.split('\r\n') if h.strip()]
    header_set = set(headers)
    # Use the hash as a seed for deterministic permutation
    # Ensure the seed is positive and within a reasonable range
    seed = abs(hash_id) % (2**31 - 1)
    
    # Create a random number generator with the seed
    random.seed(seed)
    
    # Create a copy and shuffle it deterministically
    permuted_headers = headers.copy()
    while len(header_set) > 1:
        random.shuffle(permuted_headers)
        # Return the permutation as a comma-separated string
        # return ','.join(permuted_headers)
        permuted_header = ("\r\n".join(permuted_headers) + "\r\n")
        # print("-----------")
        # print(permuted_header)
        if permuted_header != order.to_string():
            break

    if len(header_set) <= 1:
        # If all headers are the same, return the original order
        return order.to_string()
    return permuted_header
   