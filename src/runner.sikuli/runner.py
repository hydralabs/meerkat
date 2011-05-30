import sys
import os

flash_player = sys.argv[1]
swf_to_play = sys.argv[2]

test_timeout = 10

result = 'pending'

openApp(flash_player)
switchApp(flash_player)

def open_swf():
	type("O", KEY_SHIFT + KEY_CMD)
	paste('file://' + os.getcwd() + os.path.sep + swf_to_play)
	click(find("1306738115396.png"))

def onFailure(event):
	global result
	
	event.region.stopObserver()
	
	result = 'failure'	



def get_test_result():
	onAppear("1306740001745.png", onFailure)
	
	observe(test_timeout)

open_swf()
get_test_result()
closeApp(flash_player)

print result