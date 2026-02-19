import random

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



def get_mutation(order):
    hash_id = hash(order.get_root())
    headers = [h.strip() for h in order.split(',') if h.strip()]
    # Use the hash as a seed for deterministic permutation
    # Ensure the seed is positive and within a reasonable range
    seed = abs(hash_id) % (2**31 - 1)
    
    # Create a random number generator with the seed
    rng = random.Random(seed)
    
    # Create a copy and shuffle it deterministically
    permuted_headers = headers.copy()
    rng.shuffle(permuted_headers)
    
    # Return the permutation as a comma-separated string
    # return ','.join(permuted_headers)
    permuted_header = (",".join(permuted_headers) + ",")
    return permuted_header
   