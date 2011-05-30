import sys
import os

print sys.argv
print os.getcwd()

flash_player = sys.argv[1]
swf_to_play = sys.argv[2]

openApp(flash_player)
switchApp(flash_player)
r = Region(0,0,1204,760)

m = r.find("foo.png")
click(m)
click(m.below(20))

click(r.find("Address-1.png").right(30))

paste('file://' + os.getcwd() + os.path.sep + swf_to_play)
click(r.find("1306733774793.png"))