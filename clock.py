from multiprocessing import Value, Lock
from threading import Timer
from datetime import datetime, timedelta
import ctypes

class Clock:
    def __init__(self, shared_time=None, lock=None):
        self._fastTime = datetime.now()
        self._shared_time = shared_time
        self._lock = lock
        self._incTimer = Timer(1, self._incTime)
        self._speed = 1
        self._incTimer.start()
        self._update_shared_time()
        
    def _incTime(self, sec=1):
        self._speed = sec
        self._incTimer = Timer(sec, self._incTime, args=[self._speed])
        self._incTimer.start()
        self._fastTime += timedelta(seconds=1)
        self._update_shared_time()
    
    def _update_shared_time(self):
        """Update the shared timestamp that all processes read"""
        if self._shared_time is not None and self._lock is not None:
            with self._lock:
                self._shared_time.value = self._fastTime.timestamp()
    
    def getTime(self):
        return self._fastTime.strftime("%H:%M:%S")
    
    def getTimeObj(self):
        return self._fastTime
    
    def normalSpeed(self):
        if self._incTimer.is_alive():
            self._incTimer.cancel()
        self._incTime()
    
    def tenTimesSpeed(self):
        if self._incTimer.is_alive():
            self._incTimer.cancel()
        self._incTime(0.1)
    
    def endTimer(self):
        self._incTimer.cancel()
    
    def getSpeed(self):
        return self._speed
    




# Everyone Else needs this.
# from multiprocessing import Value, Lock
# from datetime import datetime
# import ctypes
# import time

# def worker_process_1(shared_timestamp, lock):
#     """A worker that only READS the clock"""
#     while True:
#         with lock:
#             timestamp = shared_timestamp.value
        
#         dt = datetime.fromtimestamp(timestamp)
#         print(f"Worker 1 sees: {dt.strftime('%H:%M:%S')}")
#         time.sleep(0.5)


# # worker2.py