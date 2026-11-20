import os

import streamlit as st
import numpy as np 
import joblib
import requests # to pass post 
from tensorflow.keras.models import load_model 
from PIL import Image 
from tensorflow.keras.preprocessing import image
import google.generativeai as genai 

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set the GEMINI_API_KEY environment variable.")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name = "gemini-2.0-flash")

chat = model.start_chat(history=[])

ml = load_model("D:\\Projects\\Demo-covid\\Data\\covid_pneu_model.h5", compile=False)


classs=["Covid19","Normal","Pneumonia"]
st.title("🫁 Penumonia/Covid Diagnosis System ⚕️")

upload = st.file_uploader("Upload a Image", type = ["png", "jpg", "jpeg"])
if upload:
    img = Image.open(upload).convert("RGB") # open img and convert to RGB 
    img = img.resize((224,224))
    st.image(img,use_column_width = True) 
    img = image.img_to_array(img)
    imgg = np.expand_dims(img , axis = 0) /255.0

    prd = ml.predict(imgg)
    res = np.argmax(prd)
    cl = classs[res]
    st.write(cl)
    if (cl == "Normal"):
        st.success("You are Healthy")
    else:
        st.subheader("👩‍⚕️ Diagnois⚕️")
        Age = st.slider("Age",0,80)
        Gen = st.selectbox("Gender",['Female','Male'])
        fv = st.selectbox("Fever (Yes/No)", ['Yes', 'No'])
        co = st.selectbox("Cough (Yes/No)", ['Yes', 'No'])
        ft = st.selectbox("Fatigue (Yes/No)", ['Yes', 'No'])
        br = st.selectbox("Breathlessness (Yes/No)", ['Yes', 'No'])
        cm = st.selectbox("Comorbidity (Yes/No)", ['Yes', 'No'])
        stt = st.selectbox("Stage", ['mild', 'moderate', 'severe'])
        tp = st.selectbox("Type", ['viral', 'Bacteria'])
        ts = st.slider("Tumor_size", 0,5)

        gn_num = 1 if Gen=="Male" else 0
        fv_num = 1 if fv =="Yes" else 0 
        cf_num = 1 if co =="Yes" else 0 
        fat = 1 if ft=="Yes" else 0
        brt_num = 1 if br =="Yes" else 0 
        cm_num =1 if cm =="Yes" else 0 
        slt_num = 0 if stt == "mild" else 1 if stt =="moderate" else 2 
        tp_num = 0 if tp=="viral" else 1 

        data_inp = {
            "Age":Age,
            "Gender":gn_num,
            "Fever":fv_num,
            "Cough":cf_num ,
            "Fatigue":fat,
            "Breathlessness":brt_num,
            "Comorbidity":cm_num, 
            "Stage":slt_num, 
            "Type":tp_num,
            "Tumor_Size":ts
          
        }
    if(st.button("Predict")):

        res = requests.post("http://127.0.0.1:8000/predict" , json = data_inp)
        response = res.json()
        st.write("Prediction : ",response["Prediction"])
            
        if (response["Prediction"] > 0.5):
            prompt = "Suggest a lifestyle habit to overcome "
            res = chat.send_message(prompt)
            st.markdown("AI Suggestions")
        
            st.markdown(res.text)
    
# feedback form 
# we need to create a session 
import streamlit as st 
import joblib

show = st.checkbox("Feedback" , ["Feedback"])
if show:
   
# Load models once (at the top)
    ml = joblib.load("cmnts.pkl")
    vec = joblib.load("vector.pkl")

# Sidebar layout for feedback (always visible)
    st.sidebar.title("📝 Comment Analyzer ")

    rate = st.sidebar.slider("Rate Us", 0, 7)
    cmnt = st.sidebar.text_area("Enter Your Comments")
    
    inp = st.button("Analyzer")
    if inp:
        if cmnt.strip() != "":
            sentiment = {
                1: "Positive Feedback 😊",
                0: "Neutral Feedback 😉",
                -1: "Negative Feedback 😑"
            }

            v = vec.transform([cmnt])
            prd = ml.predict(v)[0]
            if prd in sentiment:
                st.sidebar.success("Your Feedback is :" + sentiment[prd])
            
        else:
            st.sidebar.warning("⚠️ Please enter a comment before analyzing.")