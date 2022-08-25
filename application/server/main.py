# -*- coding: utf-8 -*-
"""Copie de Testing TFLite model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hJ8VotXBW7R-JTxB70oMFAGKPCB3q7wH

# Testing TensorFlow Lite models

This notebooks shows some ways for debugging TensorFlow Lite models and comparing them with the original implementations in TensorFlow.

For more details, take a look at blog posts:

- [Testing TensorFlow Lite image classification model](https://thinkmobile.dev/testing-tensorflow-lite-image-classification-model/) - converting TensorFlow to TensorFlow Lite and comparing models side by side.
- [Automate testing of TensorFlow Lite model implementation](https://thinkmobile.dev/automate-testing-of-tensorflow-lite-model-implementation/) - Testing TensorFlow Lite model on Android app with Espresso and instrumented tests.

### How accurate is this notebook?

It's worth to mention, that this notebook shows just some basic ideas for eye-comparison between TensorFlow and TensorFlow Lite models. It doesn't check them for speed and any other factor of performance and doesn't do any accurate side-by-side comparison. But still can be helpful with answering the question "why a model implemented on the app doesn't work the same like on notebook?".

## TensorFlow 2.0 and Colaboratory

This notebook can be executed in Colaboratory. It requires some changes to make it working on Docker environment described in linked blog post.

Examples presented in this notebook are built on top of TensorFlow 2.0 stable version.

### GPU support
The good thing about Colab is that it supports GPU envinronment without additional work. Just open **Runtime -> Change runtime type** and make sure that GPU is selected. The training process of this notebook should be about 3 times faster than on CPU env.
"""

#!pip install tensorflow-gpu
#!pip install tensorflow_hub
# !pip install git+https://github.com/RegisAmon/colabcode.git
# !pip3 install fastapi uvicorn Pillow
# !pip install -r requirements.txt
# !pip install python-multipart
# !pip install pipreqs

import cv2
from glob import glob
from pathlib import Path

#from utils import plot
from fastapi import FastAPI, File, UploadFile

#import torch
#import warnings
#warnings.filterwarnings("ignore")

"""# Initilisation API"""



#from __future__ import absolute_import, division, print_function, unicode_literals

#import matplotlib.pylab as plt
import tensorflow as tf
#import tensorflow_hub as hub
import numpy as np

"""For better data visualization we'll use [Pandas library](https://pandas.pydata.org/)."""

#import pandas as pd

# Increase precision of presented data for better side-by-side comparison
#pd.set_option("display.precision", 8)

print("Version: ", tf.__version__)
print("Hub version: ", hub.__version__)
print("Eager mode: ", tf.executing_eagerly())
print("GPU is", "available" if tf.test.is_gpu_available() else "NOT AVAILABLE")

"""# Load TFLite model

Load TensorFlow lite model with interpreter interface.
"""


# Load TFLite model and see some details about input/output
#from __future__ import absolute_import, division, print_function, unicode_literals
#!wget https://s3.eu-central-1.amazonaws.com/lms-lyon.fr/modelSavedOptimized.tar
#!tar -xvf "/content/modelSavedOptimized.tar" -C "/content/"  
import matplotlib.pylab as plt
import tensorflow as tf
#import tensorflow_hub as hub
import numpy as np


tflite_interpreter = tf.lite.Interpreter(model_path="modelSavedOptimized.tflite")
tflite_interpreter.allocate_tensors()

input_details = tflite_interpreter.get_input_details()
output_details = tflite_interpreter.get_output_details()

# print("== Input details ==")
# print("name:", input_details[0]['name'])
# print("shape:", input_details[0]['shape'])
# print("type:", input_details[0]['dtype'])

# print("\n== Output details ==")
# print("name:", output_details[0]['name'])
# print("shape:", output_details[0]['shape'])
# print("type:", output_details[0]['dtype'])




"""# Test"""

import numpy as np
from skimage.transform import resize
import cv2

def video_mamonreader(cv2,filename):
    frames = np.zeros((30, 160, 160, 3), dtype=np.float)
    i=0
    print(frames.shape)
    vc = cv2.VideoCapture(filename)
    #vc = cv2.cvtColor(vc, cv2.COLOR_BGR2GRAY)
    if vc.isOpened():
        rval , frame = vc.read()
    else:
        rval = False
    
    frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frm = resize(frame,(160,160,3))
    frm = np.expand_dims(frm,axis=0)
    if(np.max(frm)>1):
        frm = frm/255.0
    frames[i][:] = frm
    i +=1
    print("reading video")
    while i < 30:
        rval, frame = vc.read()
        frm = resize(frame,(160,160,3))
        frm = np.expand_dims(frm,axis=0)
        if(np.max(frm)>1):
            frm = frm/255.0
        frames[i][:] = frm
        i +=1
        print(i)
    return frames



def pred_fight(video,acuracy=0.85):
  ysvid2 = video_mamonreader(cv2,video)

  ysdatav2 = np.zeros((1, 30, 160, 160, 3), dtype=np.float32)

  ysdatav2[0][:][:] = ysvid2
  #print(ysvid2.shape)

  tflite_interpreter.set_tensor(input_details[0]['index'], ysdatav2)


  #val_image_batch = np.zeros((30, 160, 160, 3), dtype=np.float)
  #tflite_interpreter.set_tensor(input_details[0]['index'], val_image_batch)

  tflite_interpreter.invoke()

  tflite_model_predictions = tflite_interpreter.get_tensor(output_details[0]['index'])
    
    
  if tflite_model_predictions[0][1] >=acuracy:
      return True , tflite_model_predictions[0][1]
  else:
      return False , tflite_model_predictions[0][1]

#

import time

millis = int(round(time.time() * 1000))
print("started at " , millis)
predaction = pred_fight(video="fight2.mp4",acuracy=0.9)
print(predaction)
millis2 = int(round(time.time() * 1000))
print("time processing " , millis2 - millis)

def main_fight(vidoss):
    import time
    vid = video_mamonreader(cv2,vidoss)
    datav = np.zeros((1, 30, 160, 160, 3), dtype=np.float)
    datav[0][:][:] = vid
    millis = int(round(time.time() * 1000))
    #print(millis)
    f , precent = pred_fight(vidoss,acuracy=0.9)
    millis2 = int(round(time.time() * 1000))
    #print(millis2)
    res_mamon = {'fight':f , 'precentegeoffight':str(precent)}
    res_mamon['processing_time'] =  str(millis2-millis)
    return res_mamon



"""# API

"""

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from PIL import Image
import requests
from io import BytesIO
import cv2
from glob import glob
from pathlib import Path




app=FastAPI()


@app.post("/mainfight/")
def mainfight(url):
        res = main_fight(url)
      
 
        return {'label': res }


if __name__ == "__main__":
    uvicorn.run(app, debug=True)
