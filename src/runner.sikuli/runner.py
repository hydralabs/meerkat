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
    click(find("1306738115396.png"))


def onFailure(event):
    global result
    
    event.region.stopObserver()
    
    result = 'failure'



def onSuccess(event):
    global result

    event.region.stopObserver()

    result = 'success'



def get_test_result():
    onAppear("failure.png", onFailure)
    onAppear("success.png", onSuccess)

    observe(test_timeout)



open_swf()

try:
    get_test_result()
finally:
    type("q", KEY_CMD)


print result
