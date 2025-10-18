** FOR TIMER TO WORK IN INDIVIDUAL MODULE **

The following three lines are necessary at the top of the file:
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
import clock

You can then grab the time using clock.clock.getTime() or clock.clock.getTimeNoSecs()
BE SURE to end the timer by calling clock.clock.endTimer() AFTER root.mainloop() 
or else your program will be stuck in an infinite look updating the time.

Look at CTC_Office/CTC_UI.py for an example.