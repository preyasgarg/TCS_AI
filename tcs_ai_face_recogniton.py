# -*- coding: utf-8 -*-
"""TCS_AI_face_recogniton.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O5mDT-ySFsAn_zxmTjXrf24K52iLY4OB

# Step 1 - Import the dataset

- Upload the dataset file to google drive.
- Copy the dataset for google drive to loacal directory.
- Parse the JSON file to reveal the data.
- Download the images from the link provided in the json file.
- Save the images into appropriate directory
"""
"""
#this where json is read through drive
from google.colab import drive
drive.mount('/content/drive')

!cp 'drive/My Drive/TCS_HUMAN_AIN/Face_Recognition.json' '.'
!cp 'drive/My Drive/TCS_HUMAN_AIN/Indian_Number_plates.json' '.'
"""
import json
data = []
with open('Face_Recognition.json') as f:
  for line in f:
    data.append(json.loads(line))

import os
os.mkdir('faces')
os.mkdir('images')

import requests
temp = 0
for line in data:
  f = open('images/'+'%04d'%temp + '.jpg','wb')
  f.write(requests.get(line['content']).content)
  f.close()
  temp+=1



"""# Step 2 - First part of the network (face Detector)

- As this is **Pseudo Code so mathias detector**.
- Leave appropriate margin around face while cropping.
- Later in the final Implementation a better face detector will be used.
"""

#instead of this mathias Detector, FaceNet will be used to acheive higher no. of detecitons

import os
import cv2
import dlib
import numpy as np
import argparse
from keras.utils.data_utils import get_file
import shutil

if os.path.isdir('mathais_face_detected'):
  shutil.rmtree('mathais_face_detected')
os.mkdir('mathais_face_detected')


def main():
    depth = 16
    k = 8
    margin = 0.4

    # for face detection
    detector = dlib.get_frontal_face_detector()

    # load model and weights
    img_size = 256
    temp = os.listdir("images")
    temp.sort()
    for fimg in temp:
        print(fimg)
        img = cv2.imread("images/"+fimg)
        if not(img is None):
          input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
          img_h, img_w, _ = np.shape(input_img)

          # detect faces using dlib detector
          detected = detector(input_img, 1)
          faces = np.empty((len(detected), img_size, img_size, 3))

          if len(detected) > 0:
              for i, d in enumerate(detected):
                  x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
                  xw1 = max(int(x1 - margin * w), 0)
                  yw1 = max(int(y1 - margin * h), 0)
                  xw2 = min(int(x2 + margin * w), img_w - 1)
                  yw2 = min(int(y2 + margin * h), img_h - 1)
                  faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))
                  cv2.imwrite("mathais_face_detected/"+str(i)+'_'+fimg, faces[i, :, :, :])

if __name__ == '__main__':
    main()



"""# Step 3.1 - First(Pseudo) part of the network (face Detector)

- As this i just a pseuode implementation so i used labels to crop out face for training other network.
- Leave appropriate margin around face while cropping.
- Later in the final Implementation a better face detector will be used.
- Convert the dataset of labels into pandas dtaframe for easy use.
"""

IMAGE_SIZE = 64

if not (os.path.isdir('faces_bo')):
  os.mkdir('faces_bo')
images = os.listdir('images')
images.sort()
import cv2
temp=0
datasheet = []
for i in range(len(images)):
  im = cv2.imread('images/'+images[i])
  if not (im is None) and images[i] != '0047.jpg':
    for j in data[i]['annotation']:
      x1 = int(j['points'][0]['x'] * j['imageWidth'])
      y1 = int(j['points'][0]['y'] * j['imageHeight'])
      x2 = int(j['points'][1]['x'] * j['imageWidth'])
      y2 = int(j['points'][1]['y'] * j['imageHeight'])
      x_bo = int((x2-x1)*0.2)
      y_bo = int((y2-y1)*0.2)
      if (x1-x_bo)>0:
        x1 = x1-x_bo
      else:
        x1=0
      if (y1-y_bo)>0:
        y1 = y1-y_bo
      else:
        y1=0
      if (x2+x_bo)<j['imageWidth']:
        x2 = x2+x_bo
      else:
        x2=j['imageWidth']
      if (y2+y_bo)<j['imageHeight']:
        y2 = y2+y_bo
      else:
        y2=j['imageHeight']
      face_im = im[y1:y2,x1:x2]
      temp_list = j['label'][:]
      temp_list.sort()
      if len(temp_list)>0 and temp_list[0].startswith('Emo'):
        temp_list.insert(0,'Ethinicity_unknown')
        temp_list.insert(0,'Age_unknown')
      if 'Not_Face' in temp_list:
        temp_list = ['Not_Face'] #remeber to use 28(face_image)
      if len(temp_list) == 5: #69th image have a label with 2 ethinicity's
        face_im = cv2.resize(face_im,(IMAGE_SIZE,IMAGE_SIZE))
        cv2.imwrite('faces_bo/'+'%04d'%temp + '.jpg',face_im)
        temp_list1 = temp_list[:2]+temp_list[3:]
        temp_list1.insert(0,'faces_bo/'+'%04d'%temp + '.jpg')
        temp_list1.insert(0,'%04d'%temp + '.jpg')
        temp_list1.insert(0,images[i])
        datasheet.append(temp_list1)
        temp+=1
        cv2.imwrite('faces_bo/'+'%04d'%temp + '.jpg',face_im)
        temp_list2 = temp_list[:1]+temp_list[2:]
        temp_list2.insert(0,'faces_bo/'+'%04d'%temp + '.jpg')
        temp_list2.insert(0,'%04d'%temp + '.jpg')
        temp_list2.insert(0,images[i])
        datasheet.append(temp_list2)
        temp+=1
      else:
        try:
          face_im = cv2.resize(face_im,(IMAGE_SIZE,IMAGE_SIZE)) # one face image can't be resized in 25th image
        except:
          continue
        cv2.imwrite('faces_bo/'+'%04d'%temp + '.jpg',face_im)
        temp_list.insert(0,'faces_bo/'+'%04d'%temp + '.jpg')
        temp_list.insert(0,'%04d'%temp + '.jpg')
        temp_list.insert(0,images[i])
        datasheet.append(temp_list)
        temp+=1
  else:
    print('image not read is', images[i])

import pandas as pd
df_bo = pd.DataFrame(datasheet,columns=['orig_im','face_image', 'path', 'age', 'ethinicity', 'emotion',  'gender'])

df_bo['emotion'].unique()

"""# Step 4 - Data segmentaion and Custom Augmentation for Gender Classification.

- As this i just a pseuode implementation so only trained for gender classification.
- At later stage of full implementation ethnicities, age and emotion will also be trained.
- Python and OpenCV is used.
"""

import os
os.mkdir('gender_bo')
os.mkdir('gender_bo/male')
os.mkdir('gender_bo/female')

import shutil
orig_lis = list(df_bo.orig_im)
face_lis = list(df_bo.face_image)
age_lis = list(df_bo.age)
gender_lis = list(df_bo.gender)
path_lis = list(df_bo.path)
male = 0
female = 0
for i in range(len(gender_lis)):
  #print(gender_lis[i])
  if gender_lis[i] == 'G_Male':
    shutil.copy2(path_lis[i],'gender_bo/male')
    #print(gender_lis[i])
    male +=1
  elif gender_lis[i] == 'G_ Female':
    shutil.copy2(path_lis[i],'gender_bo/female')
    #print(gender_lis[i])
    female +=1

"""# Step 4.1 - Data scaling"""

import tensorflow as tf
def central_scale_images(X_imgs, scales):
    # Various settings needed for Tensorflow operation
    boxes = np.zeros((len(scales), 4), dtype = np.float32)
    for index, scale in enumerate(scales):
        x1 = y1 = 0.5 - 0.5 * scale # To scale centrally
        x2 = y2 = 0.5 + 0.5 * scale
        boxes[index] = np.array([y1, x1, y2, x2], dtype = np.float32)
    box_ind = np.zeros((len(scales)), dtype = np.int32)
    crop_size = np.array([IMAGE_SIZE, IMAGE_SIZE], dtype = np.int32)
    
    X_scale_data = []
    tf.reset_default_graph()
    X = tf.placeholder(tf.float32, shape = (1, IMAGE_SIZE, IMAGE_SIZE, 3))
    # Define Tensorflow operation for all scales but only one base image at a time
    tf_img = tf.image.crop_and_resize(X, boxes, box_ind, crop_size)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        
        for img_data in X_imgs:
            batch_img = np.expand_dims(img_data, axis = 0)
            scaled_imgs = sess.run(tf_img, feed_dict = {X: batch_img})
            X_scale_data.extend(scaled_imgs)
    
    X_scale_data = np.array(X_scale_data, dtype = np.float32)
    return X_scale_data

"""# Step 4.2 - Data Translation"""

from math import ceil, floor

def get_translate_parameters(index):
    if index == 0: # Translate left 20 percent
        offset = np.array([0.0, 0.2], dtype = np.float32)
        size = np.array([IMAGE_SIZE, ceil(0.8 * IMAGE_SIZE)], dtype = np.int32)
        w_start = 0
        w_end = int(ceil(0.8 * IMAGE_SIZE))
        h_start = 0
        h_end = IMAGE_SIZE
    elif index == 1: # Translate right 20 percent
        offset = np.array([0.0, -0.2], dtype = np.float32)
        size = np.array([IMAGE_SIZE, ceil(0.8 * IMAGE_SIZE)], dtype = np.int32)
        w_start = int(floor((1 - 0.8) * IMAGE_SIZE))
        w_end = IMAGE_SIZE
        h_start = 0
        h_end = IMAGE_SIZE
    elif index == 2: # Translate top 20 percent
        offset = np.array([0.2, 0.0], dtype = np.float32)
        size = np.array([ceil(0.8 * IMAGE_SIZE), IMAGE_SIZE], dtype = np.int32)
        w_start = 0
        w_end = IMAGE_SIZE
        h_start = 0
        h_end = int(ceil(0.8 * IMAGE_SIZE)) 
    else: # Translate bottom 20 percent
        offset = np.array([-0.2, 0.0], dtype = np.float32)
        size = np.array([ceil(0.8 * IMAGE_SIZE), IMAGE_SIZE], dtype = np.int32)
        w_start = 0
        w_end = IMAGE_SIZE
        h_start = int(floor((1 - 0.8) * IMAGE_SIZE))
        h_end = IMAGE_SIZE 
        
    return offset, size, w_start, w_end, h_start, h_end

def translate_images(X_imgs):
    offsets = np.zeros((len(X_imgs), 2), dtype = np.float32)
    n_translations = 4
    X_translated_arr = []
    
    tf.reset_default_graph()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(n_translations):
            X_translated = np.zeros((len(X_imgs), IMAGE_SIZE, IMAGE_SIZE, 3), 
				    dtype = np.float32)
            X_translated.fill(1.0) # Filling background color
            base_offset, size, w_start, w_end, h_start, h_end = get_translate_parameters(i)
            offsets[:, :] = base_offset 
            glimpses = tf.image.extract_glimpse(X_imgs, size, offsets)
            
            glimpses = sess.run(glimpses)
            X_translated[:, h_start: h_start + size[0], \
			 w_start: w_start + size[1], :] = glimpses
            X_translated_arr.extend(X_translated)
    X_translated_arr = np.array(X_translated_arr, dtype = np.float32)
    return X_translated_arr

"""# Step 4.3 - Data rotation"""

def rotate_images(X_imgs):
    X_rotate = []
    tf.reset_default_graph()
    X = tf.placeholder(tf.float32, shape = (IMAGE_SIZE, IMAGE_SIZE, 3))
    k = tf.placeholder(tf.int32)
    tf_img = tf.image.rot90(X, k = k)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for img in X_imgs:
            for i in range(3):  # Rotation at 90, 180 and 270 degrees
                rotated_img = sess.run(tf_img, feed_dict = {X: img, k: i + 1})
                X_rotate.append(rotated_img)
        
    X_rotate = np.array(X_rotate, dtype = np.float32)
    return X_rotate

"""# Step 4.4 - Data Flipping and Transpose"""

def flip_images(X_imgs):
    X_flip = []
    tf.reset_default_graph()
    X = tf.placeholder(tf.float32, shape = (IMAGE_SIZE, IMAGE_SIZE, 3))
    tf_img1 = tf.image.flip_left_right(X)
    tf_img2 = tf.image.flip_up_down(X)
    tf_img3 = tf.image.transpose_image(X)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for img in X_imgs:
            flipped_imgs = sess.run([tf_img1, tf_img2, tf_img3], feed_dict = {X: img})
            X_flip.extend(flipped_imgs)
    X_flip = np.array(X_flip, dtype = np.float32)
    return X_flip

"""# Step 5 - Storing data into numpy arrays
- More data augmentation techniques will be done in final implementation.
- Once data is augmented store them in numpy array and delete them from dynamic memory.
"""

import numpy as np

male = os.listdir('gender_bo/male')
male.sort()
X_male = np.zeros((len(male),IMAGE_SIZE,IMAGE_SIZE,3))
count= 0
for i in male:
  temp = cv2.imread('gender_bo/male/'+i)
  X_male[count,:,:,:] = temp
  count+=1

male = os.listdir('gender_bo/female')
male.sort()
X_female = np.zeros((len(male),IMAGE_SIZE,IMAGE_SIZE,3))
count= 0
for i in male:
  temp = cv2.imread('gender_bo/female/'+i)
  X_female[count,:,:,:] = temp
  count+=1

"""# Step 5.1 - Scaling"""

scaled_imgs_male = central_scale_images(X_male, [0.90, 0.75, 0.80])
scaled_imgs_female = central_scale_images(X_female, [0.90, 0.75, 0.80])
np.save('scaled_imgs_male',scaled_imgs_male)
np.save('scaled_imgs_female',scaled_imgs_female)
print(X_male.shape)
print(X_female.shape)
print(scaled_imgs_male.shape)
print(scaled_imgs_female.shape)
scaled_imgs_male = None
scaled_imgs_female = None

"""# Step 5.2 - Scaling + translation"""

scaled_imgs_male = np.load('scaled_imgs_male.npy')
scaled_imgs_female = np.load('scaled_imgs_female.npy')
translated_imgs_male = translate_images(X_male)
translated_imgs_female = translate_images(X_female)
translated_scaled_imgs_male = translate_images(scaled_imgs_male)
translated_scaled_imgs_female = translate_images(scaled_imgs_female)
np.save('translated_imgs_male',translated_imgs_male)
np.save('translated_imgs_female',translated_imgs_female)
np.save('translated_scaled_imgs_male',translated_scaled_imgs_male)
np.save('translated_scaled_imgs_female',translated_scaled_imgs_female)
print(X_male.shape)
print(X_female.shape)
print(scaled_imgs_male.shape)
print(scaled_imgs_female.shape)
print(translated_imgs_male.shape)
print(translated_imgs_female.shape)
print(translated_scaled_imgs_male.shape)
print(translated_scaled_imgs_female.shape)
scaled_imgs_male = None
scaled_imgs_female = None
translated_imgs_male = None
translated_imgs_female = None
translated_scaled_imgs_male = None
translated_scaled_imgs_female = None

"""# Step 5.3 - Scaling + translation + rotation"""

scaled_imgs_male = np.load('scaled_imgs_male.npy')
scaled_imgs_female = np.load('scaled_imgs_female.npy')
translated_imgs_male = np.load('translated_imgs_male.npy')
translated_imgs_female = np.load('translated_imgs_female.npy')
translated_scaled_imgs_male = np.load('translated_scaled_imgs_male.npy')
translated_scaled_imgs_female = np.load('translated_scaled_imgs_female.npy')
rotated_imgs_male = rotate_images(X_male)
rotated_imgs_female = rotate_images(X_female)
rotated_scaled_imgs_male = rotate_images(scaled_imgs_male)
rotated_scaled_imgs_female = rotate_images(scaled_imgs_female)
rotated_translated_imgs_male = rotate_images(translated_imgs_male)
rotated_translated_imgs_female = rotate_images(translated_imgs_female)
rotated_translated_scaled_imgs_male = rotate_images(translated_scaled_imgs_male)
rotated_translated_scaled_imgs_female = rotate_images(translated_scaled_imgs_female)
np.save('rotated_imgs_male',rotated_imgs_male)
np.save('rotated_imgs_female',rotated_imgs_female)
np.save('rotated_scaled_imgs_male',rotated_scaled_imgs_male)
np.save('rotated_scaled_imgs_female',rotated_scaled_imgs_female)
np.save('rotated_translated_imgs_male',rotated_translated_imgs_male)
np.save('rotated_translated_imgs_female',rotated_translated_imgs_female)
np.save('rotated_translated_scaled_imgs_male',rotated_translated_scaled_imgs_male)
np.save('rotated_translated_scaled_imgs_female',rotated_translated_scaled_imgs_female)
print(X_male.shape)
print(X_female.shape)
print(scaled_imgs_male.shape)
print(scaled_imgs_female.shape)
print(translated_imgs_male.shape)
print(translated_imgs_female.shape)
print(translated_scaled_imgs_male.shape)
print(translated_scaled_imgs_female.shape)
print(rotated_imgs_male.shape)
print(rotated_imgs_female.shape)
print(rotated_scaled_imgs_male.shape)
print(rotated_scaled_imgs_female.shape)
print(rotated_translated_imgs_male.shape)
print(rotated_translated_imgs_female.shape)
print(rotated_translated_scaled_imgs_male.shape)
print(rotated_translated_scaled_imgs_female.shape)
scaled_imgs_male = None
scaled_imgs_female = None
translated_imgs_male = None
translated_imgs_female = None
translated_scaled_imgs_male = None
translated_scaled_imgs_female = None

rotated_imgs_male = None
rotated_imgs_female = None
rotated_scaled_imgs_male = None
rotated_scaled_imgs_female = None
rotated_translated_imgs_male = None
rotated_translated_imgs_female = None
rotated_translated_scaled_imgs_male = None
rotated_translated_scaled_imgs_female = None

"""# Step 5.4 - Scaling + translation + rotation + (flipping + transpose)"""

scaled_imgs_male = np.load('scaled_imgs_male.npy')
scaled_imgs_female = np.load('scaled_imgs_female.npy')
rotated_imgs_male = np.load('rotated_imgs_male.npy')
rotated_imgs_female = np.load('rotated_imgs_female.npy')
translated_imgs_male = np.load('translated_imgs_male.npy')
translated_imgs_female = np.load('translated_imgs_female.npy')
translated_scaled_imgs_male = np.load('translated_scaled_imgs_male.npy')
translated_scaled_imgs_female = np.load('translated_scaled_imgs_female.npy')
rotated_scaled_imgs_male = np.load('rotated_scaled_imgs_male.npy')
rotated_scaled_imgs_female = np.load('rotated_scaled_imgs_female.npy')
rotated_translated_imgs_male = np.load('rotated_translated_imgs_male.npy')
rotated_translated_imgs_female = np.load('rotated_translated_imgs_female.npy')
rotated_translated_scaled_imgs_male = np.load('rotated_translated_scaled_imgs_male.npy')
rotated_translated_scaled_imgs_female = np.load('rotated_translated_scaled_imgs_female.npy')


flipped_imgs_male = flip_images(X_male)
flipped_imgs_female = flip_images(X_female)
flipped_scaled_imgs_male = flip_images(scaled_imgs_male)
flipped_scaled_imgs_female = flip_images(scaled_imgs_female)
flipped_rotated_imgs_male = flip_images(rotated_imgs_male)
flipped_rotated_imgs_female = flip_images(rotated_imgs_female)
flipped_translated_imgs_male = flip_images(translated_imgs_male)
flipped_translated_imgs_female = flip_images(translated_imgs_female)
flipped_translated_scaled_imgs_male = flip_images(translated_scaled_imgs_male)
flipped_translated_scaled_imgs_female = flip_images(translated_scaled_imgs_female)
flipped_rotated_scaled_imgs_male = flip_images(rotated_scaled_imgs_male)
flipped_rotated_scaled_imgs_female = flip_images(rotated_scaled_imgs_female)
flipped_rotated_translated_imgs_male = flip_images(rotated_translated_imgs_male)
flipped_rotated_translated_imgs_female = flip_images(rotated_translated_imgs_female)
flipped_rotated_translated_scaled_imgs_male = flip_images(rotated_translated_scaled_imgs_male)
flipped_rotated_translated_scaled_imgs_female = flip_images(rotated_translated_scaled_imgs_female)

np.save('flipped_imgs_male',flipped_imgs_male)
np.save('flipped_imgs_female',flipped_imgs_female)
np.save('flipped_scaled_imgs_male',flipped_scaled_imgs_male)
np.save('flipped_scaled_imgs_female',flipped_scaled_imgs_female)
np.save('flipped_rotated_imgs_male',flipped_rotated_imgs_male)
np.save('flipped_rotated_imgs_female',flipped_rotated_imgs_female)
np.save('flipped_translated_imgs_male',flipped_translated_imgs_male)
np.save('flipped_translated_imgs_female',flipped_translated_imgs_female)
np.save('flipped_translated_scaled_imgs_male',flipped_translated_scaled_imgs_male)
np.save('flipped_translated_scaled_imgs_female',flipped_translated_scaled_imgs_female)
np.save('flipped_rotated_scaled_imgs_male',flipped_rotated_scaled_imgs_male)
np.save('flipped_rotated_scaled_imgs_female',flipped_rotated_scaled_imgs_female)
np.save('flipped_rotated_translated_imgs_male',flipped_rotated_translated_imgs_male)
np.save('flipped_rotated_translated_imgs_female',flipped_rotated_translated_imgs_female)
np.save('flipped_rotated_translated_scaled_imgs_male',flipped_rotated_translated_scaled_imgs_male)
np.save('flipped_rotated_translated_scaled_imgs_female',flipped_rotated_translated_scaled_imgs_female)


print(X_male.shape)
print(X_female.shape)
print(scaled_imgs_male.shape)
print(scaled_imgs_female.shape)
print(translated_imgs_male.shape)
print(translated_imgs_female.shape)
print(rotated_imgs_male.shape)
print(rotated_imgs_female.shape)
print(flipped_imgs_male.shape)
print(flipped_imgs_female.shape)
print(translated_scaled_imgs_male.shape)
print(translated_scaled_imgs_female.shape)
print(rotated_scaled_imgs_male.shape)
print(rotated_scaled_imgs_female.shape)
print(rotated_translated_imgs_male.shape)
print(rotated_translated_imgs_female.shape)
print(flipped_scaled_imgs_male.shape)
print(flipped_scaled_imgs_female.shape)
print(flipped_rotated_imgs_male.shape)
print(flipped_rotated_imgs_female.shape)
print(flipped_translated_imgs_male.shape)
print(flipped_translated_imgs_female.shape)
print(rotated_translated_scaled_imgs_male.shape)
print(rotated_translated_scaled_imgs_female.shape)
print(flipped_translated_scaled_imgs_male.shape)
print(flipped_translated_scaled_imgs_female.shape)
print(flipped_rotated_scaled_imgs_male.shape)
print(flipped_rotated_scaled_imgs_female.shape)
print(flipped_rotated_translated_imgs_male.shape)
print(flipped_rotated_translated_imgs_female.shape)
print(flipped_rotated_translated_scaled_imgs_male.shape)
print(flipped_rotated_translated_scaled_imgs_female.shape)

scaled_imgs_male = None
scaled_imgs_female = None
flipped_imgs_male = None
flipped_imgs_female = None
translated_imgs_male = None
translated_imgs_female = None
translated_scaled_imgs_male = None
translated_scaled_imgs_female = None
rotated_imgs_male = None
rotated_imgs_female = None
rotated_scaled_imgs_male = None
rotated_scaled_imgs_female = None
rotated_translated_imgs_male = None
rotated_translated_imgs_female = None
flipped_scaled_imgs_male = None
flipped_scaled_imgs_female = None
flipped_rotated_imgs_male = None
flipped_rotated_imgs_female = None
flipped_translated_imgs_male = None
flipped_translated_imgs_female = None
rotated_translated_scaled_imgs_male = None
rotated_translated_scaled_imgs_female = None
flipped_translated_scaled_imgs_male = None
flipped_translated_scaled_imgs_female = None
flipped_rotated_scaled_imgs_male = None
flipped_rotated_scaled_imgs_female = None
flipped_rotated_translated_imgs_male = None
flipped_rotated_translated_imgs_female = None
flipped_rotated_translated_scaled_imgs_male = None
flipped_rotated_translated_scaled_imgs_female = None



"""# Step 6 - Load the augmented Data
- Diffrent kind of data augmented networks will be trained and ensemmble of them will be used in final implementation. This is just one of them.
"""

os.mkdir('data')
os.mkdir('data/train')
os.mkdir('data/train/male')
os.mkdir('data/train/female')

os.mkdir('data/validation')
os.mkdir('data/validation/male')
os.mkdir('data/validation/female')
os.mkdir('models')

a = np.load('flipped_rotated_scaled_imgs_male.npy')
b = np.load('flipped_rotated_scaled_imgs_female.npy')
for i,j in enumerate(a):
  cv2.imwrite('data/train/male/'+str(i)+'.jpg',j)
for i,j in enumerate(b):
  cv2.imwrite('data/train/female/'+str(i)+'.jpg',j)

a = X_male
b = X_female
for i,j in enumerate(a):
  cv2.imwrite('data/validation/male/'+str(i)+'.jpg',j)
for i,j in enumerate(b):
  cv2.imwrite('data/validation/female/'+str(i)+'.jpg',j)

"""# Step 7 - Basic Imports and datagenrator.
- Do all the required imports and for **keras** use it's image generator for passing data into model.
"""

import os
import numpy as np
from keras.models import Sequential
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras import optimizers

# dimensions of our images.
img_width, img_height = IMAGE_SIZE, IMAGE_SIZE

train_data_dir = 'data/train'
validation_data_dir = 'data/validation'

# used to rescale the pixel values from [0, 255] to [0, 1] interval
datagen = ImageDataGenerator(rescale=1./255)

# automagically retrieve images and their classes for train and validation sets
train_generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=16,
        class_mode='binary')

validation_generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=32,
        class_mode='binary')#change the batch size

"""# Step 8 - Declare small model to trained from start
- Use Maxpool to decrease size instead of playing with **stride**.
- At the end use **sigmoid** as gender classification is binary else for other classification use **softmax**.
"""

model = Sequential()
model.add(Convolution2D(32, 3, 3, input_shape=(img_width, img_height,3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Convolution2D(64, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

"""# Step 9 - Compiling
- Compile the model with RMSprop optimizer instead of SGD as it is shown to work much better at small dataset 
- Use accuracy of the network the judgement parameter.
"""

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

"""# Step 10 - Declare training params
- No. of epochs
- No. of training samples
- No. of validation samples.
"""

nb_epoch = 150
nb_train_samples = 5319
nb_validation_samples = 197

"""# Step 11 - Training"""

model.fit_generator(
        train_generator,
        samples_per_epoch=nb_train_samples,
        nb_epoch=nb_epoch,
        validation_data=validation_generator,
        nb_val_samples=nb_validation_samples)

"""# Step 12- Evaluate performance of trained network"""

model.evaluate_generator(validation_generator, nb_validation_samples)

"""# Step 13 - Save the trained Model"""

model.save_weights('models/basic_cnn_150_epochs.h5')

"""# Step 14 - Transfer Learning
- Using VGG19 for transfer learning.
- Remake the **fully connected** layers of the network as per choice.
- Can use early checkpoint but not used for now.
"""

from keras import applications
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.models import Sequential, Model 
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras import backend as k 
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
from keras.layers.normalization import BatchNormalization

img_width, img_height = 256, 256
train_data_dir = "data/train"
validation_data_dir = "data/validation"
nb_train_samples = 5319 
nb_validation_samples = 197
batch_size = 32
epochs = 100

model = applications.VGG19(weights = "imagenet", include_top=False, input_shape = (img_width, img_height, 3))


# Freeze the layers which you don't want to train. Here I am freezing the first 17 layers.
for layer in model.layers[:17]:
    layer.trainable = False

#Adding custom Layers 
x = model.output
x = Flatten()(x)
x = Dense(1024, activation="relu")(x)
x = Dropout(0.5)(x)
x = Dense(256, activation="relu")(x)
predictions = Dense(1, activation="sigmoid")(x)

# creating the final model 
model_final = Model(input = model.input, output = predictions)

# compile the model (can use SGD or RMSprop)
#model_final.compile(loss = "binary_crossentropy", optimizer = optimizers.SGD(lr=0.0001, momentum=0.9), metrics=["accuracy"])
model_final.compile(loss = "binary_crossentropy", optimizer = optimizers.RMSprop(lr=0.0001), metrics=["accuracy"])

# Initiate the train and test generators with data_genrator
datagen = ImageDataGenerator(rescale=1./255)
train_generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=16,
        class_mode='binary')

validation_generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=16,
        class_mode='binary')#change the batch size

# Save the model according to the conditions  
checkpoint = ModelCheckpoint("vgg16_1.h5", monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)
#early = EarlyStopping(monitor='val_acc', min_delta=0, patience=10, verbose=1, mode='auto')


# Train the model 
model_final.fit_generator(
train_generator,
samples_per_epoch = nb_train_samples,
epochs = epochs,
validation_data = validation_generator,
nb_val_samples = nb_validation_samples,
callbacks = [checkpoint])
#callbacks = [checkpoint, early])

"""# Step 14 - Custom Model
- Similar to VGG19.
- Used same architecture as VGG but less convolution layer in each block.
- Less no. of blocks.
"""

model = Sequential()
model.add(Convolution2D(32, 3, 3, border_mode='same',input_shape=(img_width, img_height,3)))
model.add(Activation('relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Convolution2D(64, 3, 3, border_mode='same'))
model.add(Activation('relu'))
model.add(BatchNormalization(axis=-1))
model.add(Convolution2D(64, 3, 3, border_mode='same'))
model.add(Activation('relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Convolution2D(128, 3, 3, border_mode='same'))
model.add(Activation('relu'))
model.add(BatchNormalization(axis=-1))
model.add(Convolution2D(128, 3, 3, border_mode='same'))
model.add(Activation('relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

