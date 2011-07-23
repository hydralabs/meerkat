package {
    import meerkat.TestCase;

    import flash.events.NetStatusEvent;
 


    public class main extends TestCase
    {
        public var ponger:PingPonger;

        public var counter:int = 0;

        public override function run():void
        {
            this.nc.client = this;
            this.nc.connect(this.serverUrl);

        }

        public override function onNetStatus(event:NetStatusEvent):void
        {
            if (event.info.code != 'NetConnection.Connect.Success')
            {
                this.failure('Unable to connect');

                return;
            }

            this.ponger = new PingPonger(this.nc);

            this.ponger.addEventListener('done', onPingDone);
            this.ponger.start(10);
        }


        public function onPingDone(e:PingDoneEvent):void
        {
            if (!e.success)
            {
                failure(e.reason);

                return;
            }

            this.counter += 1;

            checkSuccess();
        }

        public function checkSuccess():Boolean
        {
            if (this.counter == 2)
            {
                success();

                return true;
            }

            return false;
        }

        public function ping_client(id:Number):Number
        {
            return id;
        }

        public function server_success():void
        {
            this.counter += 1;

            checkSuccess();
        }

        public function server_fail():void
        {
            failure();
        }
    }
}
