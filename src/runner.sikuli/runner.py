import sys
import os

print sys.argv
print os.getcwd()

flash_player = sys.argv[1]
swf_to_play = sys.argv[2]

openApp(flash_player)
switchApp(flash_player)
type("O", KEY_SHIFT + KEY_CMD)
paste('file://' + os.getcwd() + os.path.sep + swf_to_play)
click(find("1306738115396.png"))