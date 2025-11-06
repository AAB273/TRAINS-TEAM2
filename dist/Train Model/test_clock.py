import time
import threading

class Stopwatch:
    """A stopwatch with start, stop, reset functionality"""
    
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the stopwatch"""
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True
            self.thread = threading.Thread(target=self._update)
            self.thread.daemon = True
            self.thread.start()
            print("Stopwatch started!")
    
    def stop(self):
        """Stop the stopwatch"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1)
            print("Stopwatch stopped!")
    
    def reset(self):
        """Reset the stopwatch to 0"""
        self.elapsed_time = 0
        if self.running:
            self.start_time = time.time()
        print("Stopwatch reset!")
    
    def get_time(self):
        """Get current elapsed time in seconds"""
        if self.running:
            return time.time() - self.start_time
        else:
            return self.elapsed_time
    
    def get_formatted_time(self):
        """Get formatted time string"""
        elapsed = self.get_time()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def _update(self):
        """Update loop for displaying time"""
        while self.running:
            formatted = self.get_formatted_time()
            print(f"\r⏱️  {formatted}", end="", flush=True)
            time.sleep(0.1)  # Update more frequently for smooth display

# Usage example
def use_stopwatch():
    stopwatch = Stopwatch()
    
    print("Starting stopwatch for 5 seconds...")
    stopwatch.start()
    time.sleep(5)
    
    print("\nStopping for 2 seconds...")
    stopwatch.stop()
    time.sleep(2)
    
    print("Resuming for 3 seconds...")
    stopwatch.start()
    time.sleep(3)
    
    stopwatch.stop()
    print(f"\nFinal time: {stopwatch.get_formatted_time()}")
    
    stopwatch.reset()
    print("Reset complete!")

# use_stopwatch()