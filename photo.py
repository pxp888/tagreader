import cv2

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
import pickle
import os
import time

import reader1 as red

def loadFile(fil):
    im = Image.open(fil)
    # im = im.filter(ImageFilter.CONTOUR)
    im2 = np.array(im)
    frame = np.ones((im2.shape[0],im2.shape[1],3),np.uint8)
    frame[:,:,0] = im2[:,:,2]
    frame[:,:,1] = im2[:,:,1]
    frame[:,:,2] = im2[:,:,0]
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    return gray


bob = red.reader()


files = os.listdir(os.getcwd())
for f in files:
    if not f.lower()[-3:]=='png': continue
    im = loadFile(f)
    # gray = cv2.GaussianBlur(gray,(3,3),2)
    # thresh = bob.scan(gray)

    start = time.time()

    for i in range(1):
        im2 = bob.grid(im)
        

    print time.time() - start

    cv2.imshow(f+'g',im)
    # cv2.imshow(f,im)

cv2.waitKey()

#Hardware
# .03 .03
# .12 .09
# .46 .34



# virtual
# .29 .29
# .56 .27
# .77 .21
