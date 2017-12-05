import time
import zmq

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:9006")

while True:
	pub.send_string('Test')
	print("Sent message")
	time.sleep(1)

