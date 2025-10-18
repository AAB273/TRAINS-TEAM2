from threading import Timer
from time import strftime


class Clock:
    def __init__(self):
        self._fastTime = strftime("%H:%M:%S")
        self._incTimer = Timer(0.1, self._incTime)
        self._incTimer.start()


    def _incTime(self):
        self._incTimer = Timer(0.1, self._incTime)
        self._incTimer.start()

        hours = int(self._fastTime[:2])
        mins = int(self._fastTime[3:5])
        secs = int(self._fastTime[6:])

        secs += 1
        #increment fast time by 1 second every 100 ms

        if (secs == 60):
            secs = 0
            mins += 1

            if (mins == 60):
                mins = 0
                hours += 1

                if (hours == 24):
                    hours = 0

        self._fastTime = f"{hours:02d}:{mins:02d}:{secs:02d}"
        print(self._fastTime)

    
    def getTime(self):
        return self._fastTime
    

    def getTimeNoSecs(self):
        return self._fastTime[:5]
    

    def endTimer(self):
        self._incTimer.cancel()
    

clock = Clock()