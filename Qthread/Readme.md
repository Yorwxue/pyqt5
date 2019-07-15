+ emit can only get data passive by return function (from child thread to parent thread)
+ if you want to send data from parent thread to child thread, you can use queue

# emit
## Create thread to execute AuthWorker
+ pre-define of connection included call function and return function
+ 1. Declare target worker
``` python
self.worker = Worker()
```
+ 2. Create thread
``` python
self.thread = QtCore.QThread()
``` 
+ 3. Assign thread to execute Worker
+ It's allowed to assign multi-task to one thread.
``` python
self.worker.moveToThread(self.thread)
self.worker2.moveToThread(self.thread)
```
+ 4. Set return signal
+ Define a function to receive teh return value from child thread
``` python
self.worker.RETURN_POINT.connect(SELF_TARGET_FOUNCTION)
```
+ Declare return point in child thread used to return value to parent thread
``` python
RETURN_POINT = QtCore.pyqtSignal(str)
Note: str means return a string
```
+ 5. Combine thread with a work function
``` python
self.thread.started.connect(self.worker.run)
```

## communication between parent and child
### Call child
``` python
self.thread.start()
```
+ The entry point is define in [5. Combine thread with a work function]
### Return value from child to parent
 + Using RETURN_POINT defined in [4. Set return signal] to return a value
 ``` python
 self.RETURN_POINT.emit("byebye")
 ```
### Finish communication with child thread 
+ Note that you must finish this communication, or you can't connect with child thread next time
``` python
self.thread.quit()
```

# queue
+ Declare
``` python
from queue import Queue
self.queue = Queue()
```

+ Pass queue to child thread, when initial worker
``` python
self.auth = AuthWorker(self.queue)
```

+ Put one data to queue
``` python
self.queue.put(data)
```

+ Get data
``` python
if not self.queue.empty():
    data = self.queue.get()
```