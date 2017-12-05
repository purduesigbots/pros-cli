#import serial.tools.list_ports
import multiprocessing
import time
import zmq

#@param device: Serial port to read from
#@param port: port to bind zmq publishing socket to
#This function is intended to be its own process, continuously retrieving data read from the serial port
#And publishing them to all listeners
def pub_reads(device, port = 9002):
	ctx = zmq.Context()
	#Reads incoming messages from the cortex, publishes them
	reader_pub = ctx.socket(zmq.PUB)
	address = 'tcp://*:{}'.format(port)
	print("Attempting to connect to " + address)
	reader_pub.bind('tcp://*:{}'.format(port))
	msgs = ""

	while True:
#		try:
		msgs = device.read_all()
#		except Exception:
#			pass
		if (msgs):
			reader_pub.send(msgs)
#			print(msgs.decode('ascii'))
		time.sleep(0)	#Yield


#@param device: Serial port to write to
#@param port: Serial Share clients should push their write requests to this port. This process
#             will listen for all such requests and queue them up for writing
# This process should take raw bytes and pass them to a separate "process" (not necessarily a process),
# that both reads from and writes to the serial port
def pull_writes(device, port = 9003):
	ctx = zmq.Context()
	#Pulls messages to send to the cortex from all serial sharers
	writer_pull = ctx.socket(zmq.PULL)
	address = 'tcp://*:{}'.format(port)
	print("Attempting to connect to " + address)
	writer_pull.bind(address)


	while True:
		device.write(writer_pull.recv())
		time.sleep(0)	#Yield

#TODO: Test with this. Unused for now
'''port = [x for x in serial.tools.list_ports.comports() if x.vid is not None and
        (x.vid in [0x4d8, 0x67b] or 'vex' in x.product.lower())][0]'''




if (__name__ == "__main__"):
	class TestSend:
		count = 0

		def read_all(self):
			time.sleep(0.5)	#Simulate wait for actual read
			self.count %= 5
			msg = "{}".format(self.count)
			msg = msg.encode('ascii')
			self.count += 1
			return msg

		def write(self, msg):
			msg = msg.decode('ascii')
			print(msg)

	tester = TestSend()
	processes = [multiprocessing.Process(target=pub_reads, args=(tester,))] + [multiprocessing.Process(target=pull_writes, args=(tester,))]
	for process in processes:
		process.start()

	while (True):
		time.sleep(90) #Make sure we never end
