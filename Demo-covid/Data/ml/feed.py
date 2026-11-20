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
            st.success("Your feedback is: " + sentiment.get(prd))
        else:
            st.warning("⚠️ Please enter a comment before analyzing.")