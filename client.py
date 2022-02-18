from threading import Thread, Lock
import requests
import base64

class WorkerThread(Thread):
    def __init__(self, num, mutex, ids, results):
       # Call the Thread class's init function
       Thread.__init__(self)
       self.num = num  # thread number
       self.mutex = mutex
       
       self.ids = ids
       self.results = results
       self.timeToQuit = False

    def run(self):
        while True:
            self.mutex.acquire() # locking the mutex to access shared variables i.e. results, IDs, timeToQuit
            if self.timeToQuit and len(self.ids) == 0:
                self.mutex.release()
                return
            fetchId = -1
            if len(self.ids) > 0:
                fetchId = str(self.ids[0])
                self.ids.pop(0)
                # checking if id is already served. If so, we'll cache it.
                if fetchId in self.results:
                    print("Request is in cache ", self.results[fetchId])
                    self.mutex.release()
                    continue
                else:
                    self.results[fetchId] = 'processing' # setting the request ID processing, if it is in processing.
            else:
                self.mutex.release()
                continue
            self.mutex.release()
            self.getData(fetchId)
    
    def getData(self, id):
        id = str(id)
        authH = self.encodeBase64(id)
        response = requests.get('https://challenges.qluv.io/items/' + id,  headers={'Authorization': authH})
        self.mutex.acquire()
        print("Worker Thread ", self.num, " served id ", id, " : ", response.text)
        self.results[id] = response.text
        self.mutex.release()

    def encodeBase64(self, s):
        bytes = s.encode("ascii")
        return base64.b64encode(bytes).decode("ascii")

    def stop(self):
        self.timeToQuit = True

class Server:
    def __init__(self):
        self.ids = []
        self.numThreads = 5 # No of requests to be processed at a time
        self.mutex = Lock()
        self.results = dict() # storing the IDs in dictionary to prevent unnecessary processing
        self.workerThreads = []
        for i in range(self.numThreads):
            self.workerThreads.append(WorkerThread(i+1, self.mutex, self.ids, self.results))

    def startServer(self):
        for i in range(self.numThreads):
            self.workerThreads[i].start()

    def stopServer(self):
        for i in range(self.numThreads):
            self.workerThreads[i].stop()
        for i in range(self.numThreads):
            self.workerThreads[i].join()
        print(self.results)
    
    def processIds(self, newIds):
        self.mutex.acquire()
        for id in newIds:
            self.ids.append(id)
        self.mutex.release()
        
def Test1():
    print("Test 1")
    server = Server()
    server.startServer()
    server.processIds([i for i in range(10)])
    server.stopServer()
    print("Test 1 Completed")
    
def Test2():
    print("Test 2")
    server = Server()
    server.startServer()
    server.processIds([i for i in range(10)])
    server.processIds([i for i in range(10)])
    server.stopServer()
    print("Test 2 Completed")

Test1()
Test2()
