from rtmpy import server


class Client(server.Client):
    """
    """

    def async_server_call(self):
        from twisted.internet import defer, reactor

        d = defer.Deferred()

        reactor.callLater(0, d.callback, 'foobar')

        return d


    def makeClientCall(self):
        """
        """
        d = self.call('async_client_call', notify=True)

        def cb(result):
            if result == 'bazgak':
                self.call('server_succeed')

                return

            raise RuntimeError

        d.addCallback(cb)



class Application(server.Application):
    """
    """

    client = Client


    def onConnectAccept(self, client, *args):
        client.makeClientCall()
