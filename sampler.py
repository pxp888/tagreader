import hashlib
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import cv2
import sys


def space(im):
	im = ((im < 10)*255).astype(np.uint8)
	im = np.swapaxes(im,0,1)
	# im = np.fliplr(im)
	# im = np.flipud(im)

	out = np.ones((800,200))*0
	imx, contours, hierarchy = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	count = 0
	n = 70
	for c in contours:
		x,y,w,h = cv2.boundingRect(c)
		k = im[y:y+h,x:x+w]
		k = np.flipud(k)
		out[n:n+h,50:50+w] = k 
		n+=h
		n+=20
		# cv2.imshow(str(count),k)
		count+=1
	out = np.swapaxes(out,0,1)
	out = np.fliplr(out)
	im = ((out < 10)*255).astype(np.uint8)

	return im


def hencode(a):
    code = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    h = hashlib.md5(a).digest()[:3]
    for i in h:
        a += code[ord(i)%36]
    return a


def hcheck(a):
    o = a[:-3]
    if hencode(o)==a: return True
    return False


im = np.ones((800,1200))*255
pim = Image.fromarray(im)
draw = ImageDraw.Draw(pim)
font = ImageFont.truetype("consola.ttf", 120)

s = 'TRX457'
s = hencode(s)

draw.text((20, 325), s,fill="black", font=font)

# pim = pim.convert('RGB')
# pim.save(s+'.png')

im = np.array(pim)
im = space(im)
cv2.imshow('',im)
cv2.waitKey()

pim = Image.fromarray(im)
pim = pim.convert('RGB')
pim.save(s+'.png')


