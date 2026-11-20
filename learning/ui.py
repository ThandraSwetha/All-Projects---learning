import streamlit as st

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Adaptive AI Learning", layout="wide")

# ------------------- SESSION STATE -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "subject" not in st.session_state:
    st.session_state.subject = None
if "chapter" not in st.session_state:
    st.session_state.chapter = None
if "difficulty" not in st.session_state:
    st.session_state.difficulty = None
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "test_started" not in st.session_state:
    st.session_state.test_started = False
if "test_completed" not in st.session_state:
    st.session_state.test_completed = False
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

# ------------------- LOGIN PAGE -------------------
if not st.session_state.logged_in:
    st.title("🎓 Student Login")
    name = st.text_input("👤 Full Name")
    grade = st.text_input("🏫 Class / Grade")
    school = st.text_input("🏢 School Name")
    if st.button("🚀 Submit"):
        if not name or not grade or not school:
            st.warning("⚠️ Fill all details!")
        else:
            st.session_state.logged_in = True
            st.session_state.name = name
            st.session_state.grade = grade
            st.session_state.school = school
            st.success(f"✅ Welcome {name}!")
    st.stop()

# ------------------- SIDEBAR -------------------
st.sidebar.title("📚 Select Subject & Chapter")
subjects = {"Math": ["Functions", "Linear Equations"],
            "Physics": ["Motion", "Force"]}
st.session_state.subject = st.sidebar.selectbox("Subject", list(subjects.keys()))
st.session_state.chapter = st.sidebar.selectbox("Chapter", subjects[st.session_state.subject])
st.session_state.difficulty = st.sidebar.radio("Select Difficulty", ["Easy", "Medium", "Hard"])

if st.sidebar.button("Start Test"):
    st.session_state.test_started = True
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.test_completed = False
    st.session_state.selected_option = None

# ------------------- QUESTIONS DATA -------------------
questions_data = {
    "Easy": [
        {"q": "f(x)=x+2, x=3?", "options":["4","5","6"], "answer":"5"},
        {"q": "f(x)=x-1, x=2?", "options":["0","1","3"], "answer":"1"},
        {"q": "f(x)=2x, x=2?", "options":["2","4","6"], "answer":"4"},
        {"q": "f(x)=x+5, x=0?", "options":["0","5","10"], "answer":"5"},
        {"q": "f(x)=x-3, x=3?", "options":["0","1","-3"], "answer":"0"}
    ],
    "Medium": [
        {"q": "f(x)=2x+3, x=4?", "options":["8","11","7"], "answer":"11"},
        {"q": "f(x)=x^2+1, x=3?", "options":["9","10","11"], "answer":"10"},
        {"q": "f(x)=3x-2, x=5?", "options":["13","15","17"], "answer":"13"},
        {"q": "f(x)=x^2-2x, x=4?", "options":["8","12","10"], "answer":"8"},
        {"q": "f(x)=2x^2+1, x=2?", "options":["5","7","9"], "answer":"9"}
    ],
    "Hard": [
        {"q": "f(x)=3x^2-2x+1, x=2?", "options":["7","9","11"], "answer":"9"},
        {"q": "f(x)=x^3-2x^2+1, x=3?", "options":["16","18","20"], "answer":"16"},
        {"q": "f(3) if f(x)=x^2-2x+1?", "options":["2","4","6"], "answer":"4"},
        {"q": "f(x)=2x^3-3x+1, x=2?", "options":["3","5","7"], "answer":"3"},
        {"q": "f(x)=x^2+2x-1, x=4?", "options":["19","21","23"], "answer":"19"}
    ]
}

# ------------------- TEST TAB -------------------
if st.session_state.test_started:
    st.header(f"📝 Test - {st.session_state.subject}: {st.session_state.chapter} ({st.session_state.difficulty})")
    level = st.session_state.difficulty
    q_index = st.session_state.q_index
    questions = questions_data[level]

    if not st.session_state.test_completed:
        if q_index < len(questions):
            q = questions[q_index]
            st.write(f"**Question {q_index+1}:** {q['q']}")
            st.session_state.selected_option = st.radio("Select an option:", q["options"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Next") and st.session_state.selected_option:
                    if st.session_state.selected_option == q["answer"]:
                        st.session_state.score += 1
                    st.session_state.q_index += 1
                    st.session_state.selected_option = None
            with col2:
                if st.button("Submit Test") and st.session_state.selected_option:
                    if st.session_state.selected_option == q["answer"]:
                        st.session_state.score += 1
                    st.session_state.test_completed = True

# ------------------- RESULT -------------------
if st.session_state.test_completed:
    score = st.session_state.score
    total = len(questions_data[st.session_state.difficulty])
    percent = int((score/total)*100)

    if score <= 1:
        feedback = "😢 Needs Improvement"
    elif score <= 3:
        feedback = "😐 Keep Practicing"
    elif score == 4:
        feedback = "🙂 Good Job"
    else:
        feedback = "😃 Excellent!"

    st.subheader(f"🎉 Test Completed! Score: {score}/{total} ({percent}%)")
    st.info(feedback)

    st.markdown("### 🧠 AI Tips & Tricks to Remember")
    tips = [
        f"Understand the concept of {st.session_state.chapter} first.",
        "Write down key formulas.",
        "Try 1-2 practice questions daily.",
        "Draw diagrams where applicable."
    ]
    for t in tips:
        st.markdown(f"- {t}")

# ------------------- OTHER TABS -------------------
st.sidebar.markdown("---")
st.sidebar.title("📊 Other Tabs")
tab = st.sidebar.radio("Navigate", ["Test", "Dashboard", "Brain Games", "Feedback"])
if tab == "Dashboard":
    st.header("📊 Performance Dashboard")
    st.bar_chart({"Score": [st.session_state.score]})

elif tab == "Brain Games":
    st.header("🧩 Brain Games (Coming Soon)")
    st.info("This section will have memory and logic games to improve brain skills.")

elif tab == "Feedback":
    st.header("✉️ Feedback")
    feedback_text = st.text_area("Give your feedback here:")
    if st.button("Submit Feedback"):
        st.success("✅ Feedback submitted. Thank you!")
