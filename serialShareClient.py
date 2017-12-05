import multiprocessing
import time
import zmq
from sys import argv

class SerialShare:
	port_sub = 9002
	port_push = 9003
	__readBuff__ = multiprocessing.Queue()
	ctx = zmq.Context()
	address = "tcp://localhost"


	def __zmq_sub__(self):
		ctx = zmq.Context()	#Every process gets its own context; this is the most reliable way I've found to get this to work so far
		#Reads incoming messages from the cortex, publishes them
		self.reader_sub = ctx.socket(zmq.SUB)
		self.reader_sub.connect('{0}:{1}'.format(self.address, self.port_sub))
		self.reader_sub.setsockopt_string(zmq.SUBSCRIBE, "")	#accept all incoming messages

		while True:
			self.__readBuff__.put(self.reader_sub.recv())
			time.sleep(0)	#Yield

	def read(self):
		return self.__readBuff__.get()

	#Assume msg is a bytestring
	def write(self, msg):
		self.writer_push.send(msg)
		print(self.writer_push)

	def __init__(self):
		#Pulls messages to send to the cortex from all serial sharers
		self.writer_push = self.ctx.socket(zmq.PUSH)
		self.writer_push.connect('{0}:{1}'.format(self.address, self.port_push))

		self.processes = [multiprocessing.Process(target=self.__zmq_sub__)]
		for process in self.processes:
			process.start()



#TODO: Remove testing

if (__name__ == "__main__"):
	#Handle stdin and stdout

	ss = SerialShare()
	share_input = input(">>> ")
	while (share_input != 'q'):
		print(ss.read().decode('ascii'))
		share_input = input(">>> ")
		ss.write(share_input.encode('ascii'))

