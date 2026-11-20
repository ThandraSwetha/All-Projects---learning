import streamlit as st
from prd import fun
from PIL import Image
st.title("Image Prediction")



uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

sub = st.button("Submit")
if sub:
    img = Image.open(uploaded_image)
    st.image(img)
    res = fun()
    
    st.write(res)

