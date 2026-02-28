class Client(NetworkParty):
    def __init__(self):
        super().__init__(
            connection_mode=ConnectionMode.CONNECT,
            uri=f"tcp://localhost:1144"
        )
        self.start()

    def receive(self, message: str | bytes, sender: Optional[str]) -> None:
        # print("message", message)
        super().receive(message, "Server")

class Server(NetworkParty):
    def __init__(self):
        super().__init__(
            connection_mode=ConnectionMode.EXTERNAL,
            uri=f"tcp://localhost:{1144}"
        )
        self.start()

    def receive(self, message: str | bytes, sender: Optional[str]) -> None:
        super().receive(message, "Client")

