from rtmpy import server


class Application(server.Application):
    """
    """

    def onConnectAccept(self, client, *args):
        def cb(ret):
            if ret:
                client.call('ping_success')
            else:
                raise RuntimeError('ping failed!')

        def eb(f):
            client.call('ping_failure')

            return f


        d = client.ping()

        d.addCallback(cb)
        d.addErrback(eb)
