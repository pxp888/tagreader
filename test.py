from PIL import Image
import requests
from StringIO import StringIO
import cv2
import numpy as np 


while 1:
	response = requests.get('http://admin:aoeuaoeu4@192.168.2.139/Streaming/channels/1/picture')
	img = Image.open(StringIO(response.content))
	im = np.array(img)
	cv2.imshow('o',im)

	key = cv2.waitKey(10)
	if key != 255: # exit on ESC
		break
