# controller.py
from clock import Clock
from multiprocessing import Value, Lock
from datetime import datetime
import ctypes

class ClockController:
    """The ONLY module that should create and modify the clock"""
    
    def __init__(self):
        self.shared_timestamp = Value(ctypes.c_double, datetime.now().timestamp())
        self.lock = Lock()
        self.clock = Clock(shared_time=self.shared_timestamp, lock=self.lock)
    
    def set_normal_speed(self):
        self.clock.normalSpeed()
    
    def set_ten_times_speed(self):
        self.clock.tenTimesSpeed()
    
    def stop(self):
        self.clock.endTimer()
    
    def get_shared_timestamp(self):
        """Return the shared memory objects for other processes"""
        return self.shared_timestamp, self.lock