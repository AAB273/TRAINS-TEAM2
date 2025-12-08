from threading import Timer
from time import strftime
from datetime import datetime, timedelta


class Clock:
    def __init__(self):
        self._fastTime = datetime.now()
        self._incTimer = Timer(1, self._incTime)
        self._speed = 1
        self._incTimer.start()

        
    def _incTime(self, sec = 1):
    #defaulted to 1x speed
        self._speed = sec
        self._incTimer = Timer(sec, self._incTime, args = [self._speed])
        self._incTimer.start()
        
        self._fastTime += timedelta(seconds = 1)

    def normalSpeed(self):
        if (self._incTimer.is_alive()):
            self._incTimer.cancel()
        self._incTime()

    def tenTimesSpeed(self):
        if (self._incTimer.is_alive()):
            self._incTimer.cancel()
        self._incTime(0.1)
    

    def getTime(self):
        return self._fastTime.strftime("%H:%M:%S")
    
    
    def getTimeObj(self):
        return self._fastTime
    

    def endTimer(self):
        self._incTimer.cancel()

    def getSpeed(self):
        return self._speed
    

clock = Clock()