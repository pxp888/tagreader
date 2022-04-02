import numpy as np
import cv2
import pickle

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Input, Dense, Dropout, Flatten
from keras.models import Model, load_model
from keras.utils import np_utils

batch_size = 18
nb_classes = 36
nb_epoch = 4
img_rows, img_cols = 28, 28
pool_size = (2, 2)
kernel_size = (3, 3)

input_shape = (img_rows, img_cols, 1)


X_train = np.load('dat.npy').astype(np.float32)
y_train = np.load('tar.npy').astype(np.float32)
X_test = X_train[:2400,:,:,:]
Y_test = y_train[:2400]
X_train = X_train[2400:,:,:,:]
Y_train = y_train[2400:]

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

# convert class vectors to binary class matrices
# Y_train = np_utils.to_categorical(y_train, nb_classes)
# Y_test = np_utils.to_categorical(y_test, nb_classes)

# model = load_model('mod1.h5')

inputs = Input(shape=input_shape)
x1 = Convolution2D(36, kernel_size[0], kernel_size[1], border_mode='valid', activation='relu')(inputs)
x1 = MaxPooling2D(pool_size=pool_size)(x1)
x1 = Convolution2D(72, kernel_size[0], kernel_size[1], border_mode='valid', activation='relu')(x1)
x1 = MaxPooling2D(pool_size=pool_size)(x1)
x1 = Dropout(0.25)(x1)
x1 = Flatten()(x1)
x1 = Dense(512,activation='relu')(x1)
x1 = Dropout(0.25)(x1)
x1 = Dense(nb_classes,activation='softmax')(x1)
model = Model(inputs,x1)

model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy'])

# model.compile(loss='mse',
#               optimizer='adadelta',
#               metrics=['accuracy'])

model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epoch,
          verbose=1, validation_data=(X_test, Y_test))
model.save('mod1.h5')

out = model.predict(X_test[:36])
a = out.argmax(1)
print a.shape
for i in range(36):
	print out[i,:].argmax(), out[i,:].max()
