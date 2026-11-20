import tensorflow as tf 
from tensorflow.keras import layers,models


def build_model():
    model = models.Sequential ( [
        layers.Input(shape = (224,224,3)),  # inputlayer creattion , 3 mense ==> RGB
        layers.Conv2D(32,(3,3), activation = "relu"), #(no_of_filters , grid, Activation_function) 
        layers.MaxPooling2D(2,2) ,# grids 
        layers.Conv2D(64, (3,2) , activation = "relu"),
        layers.MaxPooling2D(2,2) ,# grids 
        layers.Conv2D(64, (3,2) , activation = "relu"), 
        layers.MaxPooling2D(2,2) ,# grids 
        # flatten layer is inportenet for evry layer
        # with out this the model will not work 
        layers.Flatten(),
        layers.Dense(128,activation = "relu"), 
        layers.Dropout(0.5),
        layers.Dense(3,activation = "softmax") # it is the hidden layer 
    ])

    # next complie  (compliew mense you will say how to work)
    model.compile( 
        optimizer = "adam", # adam mense adpative learning 
        loss = "binary_crossentropy", 
              
        metrics = ['accuracy']
        # # with out epoches the model will not work 

   )
    return model


    