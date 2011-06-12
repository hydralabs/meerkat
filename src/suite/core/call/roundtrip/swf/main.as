/**
 * Client will make a remote call to 'known_method' with args
 * ('foo', 'bar', ['baz']).
 *
 * The expected response from the server is to respond with 'ok' and in turn call
 * a client method 'client_method' with args (1, 2, 3).
 *
 * Once the client receives that call, the test is complete.
 */

package {
    import meerkat.TestCase;

    import flash.events.NetStatusEvent;
    import flash.net.Responder;



    public class main extends TestCase
    {
        private function client_onResult(result:*):void
        {
            if (result != 'ok')
            {
                this.failure('Unexpected result from client call');
            }
        }

        private function client_onStatus(info:*):void
        {
            this.failure('Client call failed with ' + info.code);
        }

        public override function run():void
        {
            var client:Object = new Object();
            var tc:* = this;

            client.client_method = function(... args):String
            {
                if (args[0] == 1 && args[1] ==  2 && args[2] == 3)
                {
                    tc.success();
                    return 'ok';
                }

                tc.failure('Unexpected args from server ' + args);

                return null;

            };

            this.nc.client = client;
            this.nc.connect(this.serverUrl)
        }

        public override function onNetStatus(event:NetStatusEvent):void
        {
            if (event.info.code != 'NetConnection.Connect.Success')
            {
                this.failure('Unable to connect');
                return;
            }

            var r:Responder = new Responder(client_onResult, client_onStatus);

            this.nc.call('known_method', r, 'foo', 'bar');
        }
    }
}
