import threading


# Thread running server processing loop
class ServerThread(threading.Thread):
    """
    A helper class to run server in a thread.

    The following snippet runs the server for 4 seconds and quit::

        server = SimpleServer()
        server_thread = ServerThread(server)
        server_thread.start()
        time.sleep(4)
        server_thread.stop()

    """
    def __init__(self, server):
        """
        :param server: :class:`pcaspy.SimpleServer` object
        """
        super(ServerThread, self).__init__()
        self.server = server
        self.running = True

    def run(self):
        """
        Start the server processing
        """
        while self.running:
            self.server.process(0.1)

    def stop(self):
        """
        Stop the server processing
        """
        self.running = False
