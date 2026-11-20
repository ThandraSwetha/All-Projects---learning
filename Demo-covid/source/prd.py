import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing import image

classs=["Covid19","Normal","Pneumonia"]

def fun():
    ml=load_model("D:\deno-covid\Data\covid_pneu_model.h5")
    img=image.load_img("D:\\deno-covid\\Data\\test\\NORMAL\\NORMAL(1267).jpg",target_size=(224, 224))
    img=image.img_to_array(img)
    img = np.expand_dims(img, axis=0)        
    img = img / 255.0

    prd=ml.predict(img)
    ind=np.argmax(prd[0])
    print(prd)
    return (classs[ind])