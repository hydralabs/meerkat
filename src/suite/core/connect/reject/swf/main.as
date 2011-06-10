/**
 * Test a simple connection attempt to a server
 */

package {
    import meerkat.TestCase;

    import flash.events.NetStatusEvent;



    public class main extends TestCase
    {
        public override function run():void
        {
            this.nc.connect(this.serverUrl)
        }

        public override function onNetStatus(event:NetStatusEvent):void
        {
            if (event.info.code == "NetConnection.Connect.Rejected")
            {
                this.success();

                return;
            }

            this.failure();
        }
    }
}
