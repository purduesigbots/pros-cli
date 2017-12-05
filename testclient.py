import time
import zmq

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:9006")
sub.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
	print(sub.recv_string())

