from threading import Timer
from time import strftime


class Clock:
    def __init__(self):
        self.fastTime = strftime("%H:%M:%S")
        self.incTimer = Timer(0.1, self.incTime)
        self.incTimer.start()


    def incTime(self):
        self.incTimer = Timer(0.1, self.incTime)
        self.incTimer.start()

        hours = int(self.fastTime[:2])
        mins = int(self.fastTime[3:5])
        secs = int(self.fastTime[6:])

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

        self.fastTime = f"{hours:02d}:{mins:02d}:{secs:02d}"
        print(self.fastTime)