import threading
from inputs import get_key

class KeyInterface(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        
    def run(self):
        print("go2")
        events = get_key()
        print(events)
        #for event in events:
        #    print(event.ev_type, event.code, event.state)
        #    self.queue.push(event)
