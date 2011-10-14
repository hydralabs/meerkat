package {
    import meerkat.TestCase;



    public class main extends TestCase
    {
        public override function run():void
        {
            this.nc.client = this;
            this.nc.connect(this.serverUrl);

        }

        public function ping_success():void
        {
            this.success();
        }

        public function ping_failure():void
        {
            this.failure();
        }
    }
}
