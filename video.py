import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from multiprocessing import Process, Queue
import urllib
import math
import time
import requests
from StringIO import StringIO
import reader1 as red
import sys

q1 = Queue()
q2 = Queue()
q3 = Queue()
p1 = 1
p2 = 1
p3 = 1
p4 = 1

def vids(q1, url, label='na'):
	vc = cv2.VideoCapture(url)
	# if url==0:
	# 	vc.set(3,1600)
	# 	vc.set(4,1200)
	# bob = red.reader()

	while 1:
		rval, frame = vc.read()
		im = frame[:,:,1]

		im, dats = red.read(im)
		q1.put((im,label))
		q2.put((dats,label))

def work(q2):
	bob = red.reader()
	while 1:
		dats, label = q2.get()
		bob.predict(dats, label)


# p1 = Process(target=vids,args=(q1,0,'webcam'))
p1 = Process(target=vids,args=(q1,"rtsp://admin:aoeuaoeu4@192.168.2.141:554/Streaming/Channels/101",'cam right 141'))
p1.start()

# p2 = Process(target=vids,args=(q1,"rtsp://admin:aoeuaoeu4@192.168.2.165:554/Streaming/Channels/101",'cam left 165'))
# p2.start()

p3 = Process(target=work,args=(q2,))
p3.start()

# p4 = Process(target=work,args=(q2,))
# p4.start()


ps = [p1, p2, p3, p4]


count = 0
stime = time.time()
while 1:
	im, url = q1.get()

	cv2.imshow(str(url),im)
	print q1.qsize(), q2.qsize()

	count += 1
	key = cv2.waitKey(1)
	if key == 32: # exit on ESC
		break

print count / (time.time() - stime)

for i in ps:
	try:
		i.terminate()
	except:
		pass


# im = ((im < 10)*255).astype(np.uint8)
# pim = Image.fromarray(im)
# pim = pim.convert('RGB')
# pim.save('last.png')
