import pandas as pd 
import numpy as np 
from sklearn.preprocessing import LabelEncoder 
from sklearn.model_selection import train_test_split 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("youtube_comments_dataset.csv")

x = df["COMMENT"]
y = df["SENTIMENT"]

# Create TF-IDF Vectorizer
ve = TfidfVectorizer(stop_words='english', max_features=1000)
xx = ve.fit_transform(x)

ml = RandomForestClassifier()

x_train ,x_test, y_train, y_test = train_test_split(xx,y,test_size=0.2)
ml.fit(x_train,y_train)

joblib.dump(ml , "cmnts.pkl")
joblib.dump(ve , "vector.pkl")

