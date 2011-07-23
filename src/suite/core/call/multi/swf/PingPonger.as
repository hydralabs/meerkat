package
{
    import flash.net.NetConnection;
    import flash.net.Responder;
    import flash.events.EventDispatcher;


    internal class PingPonger extends EventDispatcher
    {
        private var nc:NetConnection;
        private var maxCalls:uint = 0;
        private var callNo:uint = 0;
        private var id:Number;

        function PingPonger(nc:NetConnection)
        {
            this.nc = nc;
        }

        public function start(repeatCount:uint):void
        {
            this.maxCalls = repeatCount;
            this.callNo = 0;
            this.id = Math.random();

            this.sendPing();
        }

        private function sendPing():void
        {
            var onResult:Function = function(result:Number):void
            {
                if (result != id)
                {
                    stop(false, 'bad id');

                    return;
                }

                if (callNo == maxCalls)
                {
                    stop(true);

                    return;
                }

                // round and round we go.
                sendPing();
            };

            var onStatus:Function = function(info:*):void
            {
                stop(false, info.toString());
            };

            var r:Responder = new Responder(onResult, onStatus);

            this.nc.call('ping_server', r, this.id);

            this.callNo += 1;
        }

        private function stop(success:Boolean, reason:String=null):void
        {
            var e:PingDoneEvent = new PingDoneEvent('done', success, reason);

            this.dispatchEvent(e);
        }
    }
}
