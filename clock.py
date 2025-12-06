from threading import Timer
import time
from time import strftime
from datetime import datetime, timedelta


class Clock:
    def __init__(self):
        self._fastTime = datetime.now()
        self._incTimer = Timer(1, self._incTime)
        self._incTimer.start()

        
    def _incTime(self):
        self._incTimer = Timer(1, self._incTime)
        self._incTimer.start()
        
        self._fastTime += timedelta(seconds = 10)
    

    def getTime(self):
        return self._fastTime.strftime("%H:%M")
    
    
    def getTimeObj(self):
        return self._fastTime
    

    def endTimer(self):
        self._incTimer.cancel()
    

clock = Clock()