"""
A portforwarder that records the near/far data transmission to a carrays file format.
"""


import binascii
import urlparse

from twisted.protocols import portforward


port_map = {
    'rtmp': 1935
}


class DumpRecorder(object):
    """
    """

    def __init__(self, f):
        self.f = f
        self.h = open(f, 'w+')

        self.messages = {
            'peer0': 0,
            'peer1': 0
        }


    def close(self):
        self.h.close()

    def write(self, line):
        self.h.write(line + '\n')
        self.h.flush()


    def dataReceived(self, label, data):
        self.write('char %s_%d[] = {' % (label, self.messages[label]))

        self.messages[label] += 1

        for i in xrange(0, len(data), 8):
            line = ''

            for j in xrange(0, 8):
                try:
                    line += '0x' + binascii.hexlify(data[i + j]) + ', '
                except IndexError:
                    line = line[:-2] + ' };'

                    break

            if i == len(data) - j - 1:
                line = line[:-2] + ' };'

            self.write(line.strip())



class ProxyClient(portforward.ProxyClient):
    """
    """

    label = 'peer0'


    def setRecorder(self, recorder):
        self.recorder = recorder

    def dataReceived(self, data):
        portforward.ProxyClient.dataReceived(self, data)

        self.recorder.dataReceived(self.label, data)



class ProxyClientFactory(portforward.ProxyClientFactory):
    """
    """
    
    protocol = ProxyClient


    def setServer(self, server):
        portforward.ProxyClientFactory.setServer(self, server)

        self.recorder = server.recorder


    def buildProtocol(self, addr):
        protocol = portforward.ProxyClientFactory.buildProtocol(self, addr)

        protocol.setRecorder(self.recorder)

        return protocol


class ProxyServer(portforward.ProxyServer):
    """
    """

    clientProtocolFactory = ProxyClientFactory
    label = 'peer1'


    def setRecorder(self, recorder):
        self.recorder = recorder


    def dataReceived(self, data):
        portforward.ProxyServer.dataReceived(self, data)

        self.recorder.dataReceived(self.label, data)




class ProxyFactory(portforward.ProxyFactory):
    """
    """

    protocol = ProxyServer

    def __init__(self, host, port, recorder):
        self.host = host
        self.port = port
        self.recorder = recorder

    def buildProtocol(self, addr):
        protocol = portforward.ProxyFactory.buildProtocol(self, addr)

        protocol.setRecorder(self.recorder)

        return protocol



def parse_address(address):
    result = urlparse.urlparse(address)
    parsed = False

    if result[1]: # netloc
        parsed = True
        address = result[1]

    interface = 'localhost'
    port = None

    # poor mans address parsing
    if ':' not in address:
        try:
            port = int(address)
        except ValueError:
            ok = False

            if parsed:
                interface = address
                port = port_map.get(result[0], None)

                if port is not None:
                    ok = True

            if not ok:
                raise ValueError("First arg must include a port argument")
    else:
        try:
            interface, port = address.split(':')
        except ValueError:
            raise ValueError("Malformed address")

        try:
            port = int(port)
        except ValueError:
            raise ValueError("Address must include a valid port argument")

    return interface, port



if __name__ == '__main__':
    import sys

    try:
        local_interface, local_port = parse_address(sys.argv[1])
    except IndexError:
        print("First arg must be the local address to bind to")

        raise SystemExit(1)
    except ValueError, e:
        print(str(e))

        raise SystemExit(1)

    try:
        remote_interface, remote_port = parse_address(sys.argv[2])
    except IndexError:
        print("Second arg must be the remote address to bind to")

        raise SystemExit(1)
    except ValueError, e:
        print(str(e))

        raise SystemExit(1)

    try:
        dump_file = sys.argv[3]
    except IndexError:
        print("Second arg must be the dump file")

        raise SystemExit(1)


    r = DumpRecorder(dump_file)

    from twisted.internet import reactor
    from twisted.python import log

    log.startLogging(sys.stdout)


    reactor.listenTCP(local_port, ProxyFactory(remote_interface, remote_port, r), interface=local_interface)

    try:
        reactor.run()
    finally:
        r.close()
