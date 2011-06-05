/**
 * This file is a Jinja template that is generated for each SWF test.
 *
 *
 */

package meerkat
{
    import flash.display.MovieClip;
    import flash.display.Sprite;

    import flash.net.NetConnection;

    import flash.events.AsyncErrorEvent;
    import flash.events.IOErrorEvent;
    import flash.events.NetStatusEvent;
    import flash.events.SecurityErrorEvent;



    public class TestCase extends MovieClip
    {
        public var status:String;
        public var serverUrl:String = '{{ server_url }}';
        public var loggingUrl:String = '{{ logging_url }}';
        public var nc:NetConnection;


        public function TestCase()
        {
            this.status = 'pending';
            this.nc = this.buildNetConnection();

            this.run();
        }


        /**
         * Called to actually run the test
         */
        public function run():void
        {
            // test code goes here in the subclass
        }


        public function buildNetConnection():NetConnection
        {
            var nc:NetConnection = new NetConnection();

            // NetStatus
            nc.addEventListener(NetStatusEvent.NET_STATUS, function(event:NetStatusEvent):void
            {
                trace( "onNetStatus: " + event);
            });

            nc.addEventListener(NetStatusEvent.NET_STATUS, this.onNetStatus);

            // Security
            nc.addEventListener(SecurityErrorEvent.SECURITY_ERROR, function(event:SecurityErrorEvent):void
            {
                trace("onSecurityError: " + event);
            });

            nc.addEventListener(SecurityErrorEvent.SECURITY_ERROR, this.onSecurityError);

            // IOError
            nc.addEventListener(IOErrorEvent.IO_ERROR, function(event:IOErrorEvent):void
            {
                trace("onIOError: " + event);
            });

            nc.addEventListener(IOErrorEvent.IO_ERROR, this.onIOError);

            //AsyncError
            nc.addEventListener(AsyncErrorEvent.ASYNC_ERROR, function(event:AsyncErrorEvent):void
            {
                trace("onAsyncError: " + event);
            });

            nc.addEventListener(AsyncErrorEvent.ASYNC_ERROR, this.onAsyncError);

            return nc;
        }


        public function onNetStatus(event:NetStatusEvent):void
        {
            this.failure();
        }


        public function onSecurityError(event:SecurityErrorEvent):void
        {
            this.failure();
        }


        public function onIOError(event:IOErrorEvent):void
        {
            this.failure();
        }


        public function onAsyncError(event:AsyncErrorEvent):void
        {
            this.failure();
        }


        /**
         * Called to indicate a successful test run.
         */
        public function success():void
        {
            /*
            if (this.status != 'pending')
            {
                trace('Call to success when status already set')
                this.error();

                return;
            }
            */

            this._drawRect(0x00FF00);
            this.status = 'success';
        }

        /**
         * Called to indicate a failed test run.
         */
        public function failure():void
        {
            if (this.status != 'pending')
            {
                trace('Call to failure when status already set')
                this.error();

                return;
            }

            this._drawRect(0xFF0000);
            this.status = 'failure';
        }

        /**
         * Called to indicate an unexpected error in running the test.
         */
        public function error():void
        {
            // black
            this._drawRect(0x000000);
            this.status = 'error';
        }

        /**
         * Called to indicate a timeout when running the test.
         */
        public function timeout():void
        {
            // gray
            this._drawRect(0xCCCCCC);
            this.status = 'timeout';
        }

        private function _drawRect(colour:int):void
        {
            var square:Sprite = new Sprite();

            square.graphics.beginFill(colour);
            square.graphics.drawRect(0, 0, stage.stageWidth, stage.stageHeight);
            square.graphics.endFill();

            square.x = 0;
            square.y = 0;

            this.addChild(square);

        }
    }
}
