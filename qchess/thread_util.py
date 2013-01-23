import threading

# A thread that can be stopped!
# Except it can only be stopped if it checks self.stopped() periodically
# So it can sort of be stopped
class StoppableThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._stop = threading.Event()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()
