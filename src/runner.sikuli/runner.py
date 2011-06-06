import sys
import os

flash_player = sys.argv[1]
swf_to_play = sys.argv[2]

full_path = 'file://' + os.getcwd() + os.path.sep + swf_to_play

test_timeout = 10

result = 'pending'

app = App.open(flash_player)
app.focus()
wait(1)



def open_swf():
    type("O", KEY_SHIFT + KEY_CMD)
    paste(full_path)
    type("\n")



def onFailure(event):
    global result
    
    event.region.stopObserver()
    
    result = 'failure'



def onSuccess(event):
    global result

    event.region.stopObserver()

    result = 'success'



def onError(event):
    global result

    event.region.stopObserver()

    result = 'error'


def onTimeout(event):
    global result

    event.region.stopObserver()

    result = 'timeout'


def get_test_result():
    onAppear(Pattern("failure.png").exact(), onFailure)
    onAppear(Pattern("success.png").exact(), onSuccess)
    onAppear(Pattern("error.png").exact(), onError)
    onAppear(Pattern("timeout.png").exact(), onTimeout)

    observe(test_timeout)



open_swf()

try:
    get_test_result()
finally:
    type("q", KEY_CMD)


if result == 'pending':
    result = 'nomatch'

print 'RESULT:', result
