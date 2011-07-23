package
{
    import flash.events.Event;

    public class PingDoneEvent extends Event
    {
        public var success:Boolean;
        public var reason:String;

        function PingDoneEvent(type:String, success:Boolean, reason:String=null)
        {
            super(type);

            this.success = success;
            this.reason = reason;
        }
    }
}
