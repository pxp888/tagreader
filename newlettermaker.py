import cv2

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np
import pickle
import math
from multiprocessing import Process, Queue


code = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def makelet(let):
    im = np.ones((200,200))*0
    pim = Image.fromarray(im)
    draw = ImageDraw.Draw(pim)
    font = ImageFont.truetype("consola.ttf", 75)
    draw.text((90, 85), let,fill="white", font=font)
    im = np.array(pim).astype(np.uint8)
    # cv2.line(im,(300,300),(500,300),255)
    # cv2.line(im,(500,300),(500,500),255)
    # cv2.line(im,(500,500),(300,500),255)
    # cv2.line(im,(300,500),(300,300),255)
    return im


def distort(im,x,y):
    y =  y*math.pi*2
    x = 1 - x
    a = (110.0/180.0)*math.pi + y
    b = (-110.0/180.0)*math.pi + y
    c = y
    a1 = [100+math.cos(a),100+math.sin(a)]
    b1 = [100+math.cos(b),100+math.sin(b)]
    c1 = [100+math.cos(c),100+math.sin(c)]
    c2 = [100+x*math.cos(c),100+x*math.sin(c)]
    pts = np.float32( [a1,b1,c2] )
    pts1 = np.float32( [a1,b1,c1] )
    M = cv2.getAffineTransform(pts,pts1)
    k = cv2.warpAffine(im,M,(200,200))
    return k


def distort2(im,x,y):
    x = (x-.5)*19
    y = (y-.5)*19
    b1 = np.float32( [ [0,0],[10,0],[10,10],[0,10] ])
    b2 = np.float32( [ [0+x,0+y],[10+x,0+y],[10,10],[0,10] ])
    M = cv2.getPerspectiveTransform(b1,b2)
    k = cv2.warpPerspective(im,M,(400,400))
    return k


def extract(im):
    im2 = np.uint8(im.copy())
    imx, contours, hierarchy = cv2.findContours(im2,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # dat = np.ones((28,28,len(contours)))
    count = 0
    for i in contours:
        c = cv2.minEnclosingCircle(i)
        y = int(c[0][0])
        x = int(c[0][1])
        r = int(c[1]*1.3)
        a = [y-r,x-r]
        b = [y+r,x-r]
        c = [y+r,x+r]
        d = [y-r,x+r]
        box = np.float32( [a,b,c,d] )
        box2 = np.float32( [ [0,0],[28,0],[28,28],[0,28] ] )
        M = cv2.getPerspectiveTransform(box,box2)
        k = cv2.warpPerspective(im,M,(28,28))
        # dat[:,:,count] = k
        count += 1
    return k


q1 = Queue()

def hello(q1):
    cycles = 250
    size = cycles*36
    dat = np.ones((size,28,28))
    target = np.zeros((size,36))
    count = 0
    for i in range(cycles):
        for n in range(36):
            im = makelet(code[n])
            im2 = distort2(im,np.random.rand()*.8,np.random.rand()*.8)
            pic = extract(im2)
            if cycles == 1: cv2.imshow(str(n),pic)
            dat[count,:,:] = extract(pic)
            target[count,n] = 1
            count+=1
        if i%10==0: print i
    dat = np.expand_dims(dat,4)
    q1.put((dat,target))


pros = 8
pop = []
for i in range(pros):
    p1 = Process(target=hello,args=(q1,))
    p1.start()
    pop.append(p1)

dat = np.ones((0,28,28,1))
tar = np.ones((0,36))

for i in range(pros):
    d,t = q1.get()
    dat = np.append(dat,d,0)
    tar = np.append(tar,t,0)

print dat.shape, tar.shape


for i in pop:
    try:
        i.terminate()
    except:
        pass
print 'done'


np.save('dat',dat)
np.save('tar',tar)
