from rtmpy import server


class Client(server.Client):
    """
    """

    def known_method(self, *args):
        """
        """
        if args != ('foo', 'bar'):
            raise Exception('Unexpected arguments')

        self.call('client_method', 1, 2, 3)

        return 'ok'


class Application(server.Application):
    """
    """

    client = Client
