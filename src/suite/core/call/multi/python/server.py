from rtmpy import server



class Client(server.Client):
    def ping(self, callId):
        return callId


class Application(server.Application):
    """
    An application that will reject any incoming connection
    """

    client = Client
