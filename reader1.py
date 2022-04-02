import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import math
import hashlib
import time
import copy 

from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils

from PyQt4.QtNetwork import *


rad = 4
def rounder(x,y):
	x = x - rad
	y = y - rad
	c = (x*x+y*y)**.5
	return c
kernel = np.fromfunction(rounder,(rad*2,rad*2))
kernel = ((kernel < rad)*1).astype(np.uint8)
k = 31
tkernel = np.ones((k,k),np.float32)/((k**2)-1)


def pthresh(im, kernel=tkernel):
	t = cv2.filter2D(im,-1,kernel)
	thresh = (((t*.99)-im) > 15)*255
	ker = np.ones((5,5),np.uint8)
	im = cv2.erode(im,ker,iterations = 2)
	return thresh.astype(np.uint8)



def read(im, kern=kernel, target=9):
	im = pthresh(im)
	fat = cv2.resize(im,(im.shape[1]/2,im.shape[0]/2))
	fat = cv2.dilate(fat,kern,1)
	fat = ((fat > 120)*255).astype(np.uint8)
	imx, contours, hierarchy = cv2.findContours(fat.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
	dats = []
	if hierarchy is None: return im, dats
	cn = {}
	for i in range(len(hierarchy[0])):
		par = hierarchy[0][i][3]
		if par==-1:
			cn[i] = []
		else:
			cn[par].append(i)
	for i in cn:
		box = cv2.minAreaRect(contours[i])
		pts = cv2.boxPoints(box)
		w = box[1][0]
		h = box[1][1]
		ang = box[2]
		ang = (ang/180)*math.pi
		if w < h:
			temp = w
			w = h
			h = temp
			ang += math.pi*.5
		aspect = w/h
		area = w*h
		if aspect < 3: continue
		if w < 50: continue
		if w > 200: continue

		n = np.ones((fat.shape))*0
		cv2.drawContours(n,contours,i,255,-1)
		n = cv2.resize(n,(im.shape[1],im.shape[0]))

		pts = pts * 2
		x1 = 0
		x2 = 100000
		y1 = 0
		y2 = 100000
		for p in pts:
			if p[0] > x1: x1 = int(p[0])
			if p[1] > y1: y1 = int(p[1])
			if p[0] < x2: x2 = int(p[0])
			if p[1] < y2: y2 = int(p[1])
		k = im[y2:y1,x2:x1]
		n = n[y2:y1,x2:x1]
		k = (np.logical_and(k,n)*255).astype(np.uint8)
		try:
			d1 = _extract(k,ang,target)
			if d1.shape[0]==target: dats.append(d1)
			k = np.fliplr(k)
			k = np.flipud(k)
			d1 = _extract(k,ang,target)
			if d1.shape[0]==target: dats.append(d1)
		except:
			pass
		# im = (im*.5 + cv2.resize(fat,(im.shape[1],im.shape[0]))*.5 ).astype(np.uint8)
		cv2.polylines(im,np.int32([pts]),True,255)
	return im, dats





def _extract(im, ang, target=9):
	# xx = str(np.random.rand())
	# cv2.imshow(xx,im)
	cut = 60
	out = cv2.connectedComponentsWithStats(im,4,cv2.CV_32S)
	size = out[2][:,4]
	if ((size >= cut)*1).sum(0) != (target + 1):
		return np.ones(1)
	size = (size < cut)*np.arange(out[0])
	im = out[1]
	size = np.in1d(im,size)
	np.place(im,size,0)
	im = ((im > 0)*255).astype(np.uint8)
	# ker = np.ones((5,5),np.uint8)
	# im = cv2.erode(im,ker,iterations = 1)
	im = np.swapaxes(im,0,1)
	imx, contours, hierarchy = cv2.findContours(im.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
	cn = {}
	for i in range(len(hierarchy[0])):
		par = hierarchy[0][i][3]
		if par==-1:
			cn[i] = []
		else:
			cn[par].append(i)
	if len(cn) != target: return np.ones(1)
	dat = np.ones((target,28,28))
	count = 0
	for i in cn:
		c = cv2.minEnclosingCircle(contours[i])
		y = int(c[0][0])
		x = int(c[0][1])
		r = int(c[1]*2)
		a = [y + r * math.sin(ang + math.pi*1.25) , x + r * math.cos(ang + math.pi*1.25)]
		b = [y + r * math.sin(ang + math.pi*.75) , x + r * math.cos(ang + math.pi*.75)]
		c = [y + r * math.sin(ang + math.pi*.25) , x + r * math.cos(ang + math.pi*.25)]
		d = [y + r * math.sin(ang + math.pi*1.75) , x + r * math.cos(ang + math.pi*1.75)]
		box = np.float32( [a,b,c,d] )
		box2 = np.float32( [ [0,0],[28,0],[28,28],[0,28] ] )
		M = cv2.getPerspectiveTransform(box,box2)
		n = np.ones(im.shape)*0
		cv2.drawContours(n,contours,i,255,-1)
		for j in cn[i]: cv2.drawContours(n,contours,j,0,-1)
		k = cv2.warpPerspective(n,M,(28,28))
		k = np.swapaxes(k,0,1)
		dat[count,:,:] = k
		count += 1
	return dat







class reader:
	def __init__(self):
		self.model = load_model('read4.h5')
		self.code = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		print '-------------MODEL SET'
		self.tkernel = tkernel
		self.kernel = kernel


	def hencode(self,a):
		h = hashlib.md5(a).digest()[:3]
		for i in h:
			a += self.code[ord(i)%36]
		return a


	def hcheck(self, a):
		o = a[:-3]
		if self.hencode(o)==a: return True
		return False


	def predict(self,dats,url='0'):
		for dat in dats:
			dat = np.expand_dims(dat,4)
			res = self.model.predict(dat)
			res = (res * np.arange(36).reshape(1,36)).sum(1).astype(np.int32)
			cur = ''
			for i in range(res.shape[0]):
				cur += self.code[res[i]]
			cur = cur[::-1]
			if self.hcheck(cur):
				cur = url + ' : ' + cur
				print time.time(), cur
				sock = QUdpSocket()
				sock.writeDatagram(cur, QHostAddress.Broadcast, 8081)





	def show(self, im):
		im = pthresh(im)
		font = cv2.FONT_HERSHEY_SIMPLEX
		ang = 0
		imx, contours, hierarchy = cv2.findContours(im.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
		cn = {}
		for i in range(len(hierarchy[0])):
			par = hierarchy[0][i][3]
			if par==-1:
				cn[i] = []
			else:
				cn[par].append(i)

		count = 0
		dat = np.ones((len(cn),28,28,1))
		cord = []
		for i in cn:
			c = cv2.minEnclosingCircle(contours[i])
			y = int(c[0][0])
			x = int(c[0][1])
			r = int(c[1]*2)
			if r < 15: continue
			if r > 50: continue
			a = [y + r * math.sin(ang + math.pi*1.25) , x + r * math.cos(ang + math.pi*1.25)]
			b = [y + r * math.sin(ang + math.pi*.75) , x + r * math.cos(ang + math.pi*.75)]
			c = [y + r * math.sin(ang + math.pi*.25) , x + r * math.cos(ang + math.pi*.25)]
			d = [y + r * math.sin(ang + math.pi*1.75) , x + r * math.cos(ang + math.pi*1.75)]
			box = np.float32( [a,b,c,d] )
			box2 = np.float32( [ [0,0],[28,0],[28,28],[0,28] ] )
			M = cv2.getPerspectiveTransform(box,box2)
			n = np.ones(im.shape)*0
			cv2.drawContours(n,contours,i,255,-1)
			for j in cn[i]: cv2.drawContours(n,contours,j,0,-1)
			k = cv2.warpPerspective(n,M,(28,28))
			dat[count,:,:,0] = k
			cord.append((x,y))
			count += 1
		res = self.model.predict(dat)
		im = im / 3
		out = res.argmax(1)

		for i in range(len(cord)):
			let = self.code[out[i]]
			x = cord[i][0]
			y = cord[i][1]
			cv2.putText(im,str(let),(y,x),font,1,255)

		return im.astype(np.uint8)



	def grid(self, im):
		im = pthresh(im)
		font = cv2.FONT_HERSHEY_SIMPLEX
		ang = 0
		imx, contours, hierarchy = cv2.findContours(im.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
		cn = {}
		for i in range(len(hierarchy[0])):
			par = hierarchy[0][i][3]
			if par==-1:
				cn[i] = []
			else:
				cn[par].append(i)

		count = 0
		dat = []
		for i in cn:
			c = cv2.minEnclosingCircle(contours[i])
			x = int(c[0][0])
			y = int(c[0][1])
			r = int(c[1]*2)
			if r < 15: continue
			if r > 100: continue
			dat.append((x,y,r,count))
			count+=1
		dat = np.array(dat)
		# dat.view('i8,i8,i8,i8').sort(order=['f0'], axis=0)
		dim = dat.shape[0]
		dx = dat[:,0].reshape(dim,1) - dat[:,0].reshape(1,dim)
		dy = dat[:,1].reshape(dim,1) - dat[:,1].reshape(1,dim)
		rad = dat[:,2].reshape(dim,1) + dat[:,2].reshape(1,dim)
		dis = ((dx**2)+(dy**2))**.5

		valid = (dis < rad*.5)*1 + (dis > rad*.2)*1 + (dx > 0)*1 == 3
		links = np.arange(dim**2).reshape(dim,dim)[valid]
		sor = dat[:,3][links%dim]
		des = dat[:,3][links/dim]
		mapp = {}
		for i in range(sor.shape[0]):
			if not sor[i] in mapp: mapp[sor[i]] = []
			mapp[sor[i]].append(des[i])
		starts = []
		for i in range(dim):
			if not i in des:
				starts.append([i])

		mapp[3].append(1)
		mapp[5].append(3)
		while 1:
			ok = 0 
			g = []
			for i in starts:
				if i[-1] in mapp:
					ok = 1
					next = mapp[i[-1]]
					for n in next[1:]:
						s = copy.copy(i)
						s.append(n)
						g.append(s)				 		
					i.append(next[0])
			starts.extend(g)
			if ok==0: break

		target = 9 
		for i in starts:
			if len(i) > target:
				for n in range(len(i) - target+1):
					s = i[n:n+target]
					starts.append(s)

		n = []
		for i in starts:
			if len(i)==target: n.append(i)

		for i in n: print i 
		return im.astype(np.uint8)		
