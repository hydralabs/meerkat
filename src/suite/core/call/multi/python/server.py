import random

from rtmpy import server



class Client(server.Client):
    """
    """

    def ping_server(self, callId):
        return callId


    def start(self, repeat):
        self.id = random.random()
        self.callNumber = 0
        self.repeat = repeat

        from twisted.internet import reactor

        reactor.callLater(0, self.sendPing)


    def sendPing(self):
        d = self.call('ping_client', self.id, notify=True)

        def cb(result):
            if result != self.id:
                self.call('server_fail')

                return

            if self.callNumber == self.repeat:
                self.call('server_success')

                return

            self.sendPing()

            return result

        def eb(fail):
            self.call('server_fail')

            return fail

        d.addCallbacks(cb, eb)

        self.callNumber += 1


class Application(server.Application):
    """
    An application that will reject any incoming connection
    """

    client = Client


    def onConnectAccept(self, client, *args):
        client.start(10)
