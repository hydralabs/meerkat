package {
    import meerkat.TestCase;

    import flash.events.NetStatusEvent;
    import flash.net.Responder;


    public class main extends TestCase
    {
        public var callcounter:int = 0;

        public override function run():void
        {
            this.nc.connect(this.serverUrl);
            this.nc.client = this;
        }

        public override function onNetStatus(event:NetStatusEvent):void
        {
            if (event.info.code != "NetConnection.Connect.Success")
            {
                this.failure();

                return;
            }

            this.makeServerCall();
        }

        /**
         * Called from the server to test asynchronous result handling.
         */
        public function async_client_call():String
        {
            this.callcounter += 1;

            return 'bazgak';
        }

        public function server_succeed():void
        {
            // called by the server if a successful roundtrip call is made.
            this.callcounter += 1;

            this.checkSuccess();
        }


        public function checkSuccess():void
        {
            if (this.callcounter == 2)
                this.success();
        }


        public function makeServerCall():void
        {
            var onResult:Function = function(result:*):void
            {
                if (result != 'foobar')
                {
                    failure();

                    return;
                }

                checkSuccess();
            };

            var onStatus:Function = function(info:*):void
            {
                failure();
            };

            var r:Responder = new Responder(onResult, onStatus);

            this.nc.call('async_server_call', r);
        }
    }
}
