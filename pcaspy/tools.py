import threading

# Thread running server processing loop
class ServerThread(threading.Thread):
    def __init__(self, server):
        super(ServerThread, self).__init__()
        self.server = server
        self.running = True

    def run(self):
        while self.running:
            self.server.process(0.1)
    def stop(self):
        self.running = False

