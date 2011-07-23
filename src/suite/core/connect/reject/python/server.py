from rtmpy import server



class Application(server.Application):
    """
    An application that will reject any incoming connection
    """


    def onConnect(self, client, *args):
        return False
