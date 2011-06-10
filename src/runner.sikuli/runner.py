import sys
import os

flash_player = sys.argv[1]
swf_to_play = sys.argv[2]

full_path = 'file://' + os.getcwd() + os.path.sep + swf_to_play

test_timeout = 10

result = 'pending'

app = App.open(flash_player)
app.focus()
wait(0.5)



def open_swf():
    print 'Opening file:', full_path
    type("O", KEY_SHIFT + KEY_CMD)
    wait("flash_open_dialog.png")
    type(full_path)
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
    r = Region(0, 0, 400, 400)

    r.onAppear("failure.png", onFailure)
    r.onAppear("success.png", onSuccess)
    r.onAppear("error.png", onError)
    r.onAppear("timeout.png", onTimeout)

    r.observe(test_timeout)



open_swf()

try:
    get_test_result()
finally:
    type("q", KEY_CMD)


if result == 'pending':
    result = 'nomatch'

print 'RESULT:', result
