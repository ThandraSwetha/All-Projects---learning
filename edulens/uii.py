"""
EduLens - Streamlit app (single-file)
Zero-shot (BART-MNLI) classifier + T5 summarizer (T5ForConditionalGeneration)
Works after running the install commands provided.
"""

import io
import re
from typing import List, Tuple
import os

import pdfplumber
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import torch
from transformers import pipeline
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Optional: OpenAI Chat (only if OPENAI_API_KEY is set in environment)
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# Config
# -----------------------------
LABELS = [
    "Education",
    "Students",
    "Exams",
    "Scholarships",
    "College Admissions",
    "University",
    "Training",
    "Career",
    "Jobs",
    "Internships",
]

CLASSIFY_THRESHOLD = 0.55
MAX_SUMMARY_LENGTH = 120
MIN_SUMMARY_LENGTH = 30
MAX_LEN = 800         # characters to trim before classification/summarization
MAX_BLOCKS = 150
BATCH_SIZE = 16       # classification / summarization batch size

st.set_page_config(page_title="EduLens - Student News Extractor", layout="wide")

# -----------------------------
# Load models
# -----------------------------
@st.cache_resource
def load_models():
    # zero-shot classifier using BART-MNLI (stable)
    classifier_pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # T5 summarizer (we'll use T5 model & tokenizer and do batch generate)
    t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
    t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")

    # Detect device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t5_model.to(device)

    return classifier_pipe, t5_tokenizer, t5_model, device


classifier, t5_tokenizer, t5_model, device = load_models()


# -----------------------------
# Utility functions
# -----------------------------
def extract_text_from_pdf(file) -> str:
    text_pages = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)
    except Exception as e:
        st.warning(f"pdfplumber extraction failed: {e}")

    joined = "\n\n".join(text_pages).strip()
    return joined


def split_into_articles(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cleaned = []
    for ln in lines:
        if ln.isupper() and len(ln) < 60:
            continue
        cleaned.append(ln)

    combined = "\n".join(cleaned)
    articles = re.split(r"\n{2,}|\f", combined)
    articles = [a.strip() for a in articles if len(a.strip()) > 80]

    result = []
    for a in articles:
        if len(a) > 2000:
            paras = [p.strip() for p in re.split(r"\n{1,}|(?<=\.)\s{2,}", a) if len(p.strip()) > 120]
            result.extend(paras)
        else:
            result.append(a)
    return result


def create_pdf_bytes(title: str, summaries: List[Tuple[str, str, str]]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, title)
    y -= 30
    c.setFont("Helvetica", 11)

    for tag, head, summ in summaries:
        if y < 120:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 11)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"[{tag}] {head}")
        y -= 16
        c.setFont("Helvetica", 10)

        wrapped = [summ[i : i + 100] for i in range(0, len(summ), 100)]
        for ln in wrapped:
            c.drawString(margin + 10, y, ln)
            y -= 12
            if y < 80:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
        y -= 10

    c.save()
    buffer.seek(0)
    return buffer.read()


# Summarize a batch of texts using T5 (batch-safe)
def summarize_batch(texts: List[str], min_len=MIN_SUMMARY_LENGTH, max_len=MAX_SUMMARY_LENGTH) -> List[str]:
    if not texts:
        return []

    # prepare inputs with "summarize: " prefix (T5 style)
    prefixed = ["summarize: " + re.sub(r"\s+", " ", t) for t in texts]
    enc = t5_tokenizer(prefixed, return_tensors="pt", padding=True, truncation=True, max_length=512)
    input_ids = enc.input_ids.to(device)
    attention_mask = enc.attention_mask.to(device)

    # generate summaries
    gen = t5_model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=max_len,
        min_length=min_len,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True,
        no_repeat_ngram_size=2
    )

    summaries = t5_tokenizer.batch_decode(gen, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    summaries = [s.strip() for s in summaries]
    return summaries


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🤖 EduLens — Student-Focused Newspaper Analyzer 🎓")
st.markdown("Upload a newspaper PDF → extract student-related news → summarize → download notes.")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    threshold = st.slider("Classification threshold", 0.1, 0.95, CLASSIFY_THRESHOLD, 0.01)
    max_s = st.slider("Max summary length", 50, 300, MAX_SUMMARY_LENGTH, 10)
    min_s = st.slider("Min summary length", 10, 100, MIN_SUMMARY_LENGTH, 5)
    max_blocks = st.number_input("Max candidate blocks to process", min_value=20, max_value=1000, value=MAX_BLOCKS, step=10)
    batch_size = st.slider("Batch size", 4, 64, BATCH_SIZE, step=4)

# update globals from sidebar
CLASSIFY_THRESHOLD = threshold
MAX_SUMMARY_LENGTH = max_s
MIN_SUMMARY_LENGTH = min_s
MAX_BLOCKS = int(max_blocks)
BATCH_SIZE = int(batch_size)

# session state
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "raw_articles" not in st.session_state:
    st.session_state.raw_articles = []
if "filtered_articles" not in st.session_state:
    st.session_state.filtered_articles = []

tab1, tab2, tab3, tab4 = st.tabs([
    "⬇ Upload & Analyze",
    "📜 Results & Download",
    "🪙 About / Help",
    "🤖 EduLens Chatbot"
])

# -------------- TAB 1 ----------------
with tab1:
    st.header("Upload Newspaper PDF")
    uploaded = st.file_uploader("Upload PDF (newspaper)", type=["pdf"], accept_multiple_files=False)
    start_btn = st.button("Start Analysis")

    if uploaded and start_btn:
        with st.spinner("Extracting text..."):
            text = extract_text_from_pdf(uploaded)

        if not text or len(text) < 50:
            st.error("No text found. If this is a scanned PDF, text extraction failed.")
        else:
            st.success("Text extracted — splitting into articles...")
            articles = split_into_articles(text)
            st.session_state.raw_articles = articles

            total_candidates = len(articles)
            st.info(f"Found {total_candidates} candidate blocks (processing top {min(MAX_BLOCKS, total_candidates)}).")

            to_process = articles[: min(MAX_BLOCKS, total_candidates)]
            trimmed_texts = [a[:MAX_LEN] for a in to_process]

            # classification in batches
            results_filtered = []
            num = len(trimmed_texts)
            batches = [trimmed_texts[i : i + BATCH_SIZE] for i in range(0, num, BATCH_SIZE)]
            offsets = [i for i in range(0, num, BATCH_SIZE)]

            processed_count = 0
            prog = st.progress(0)
            prog_text = st.empty()

            for b_idx, (batch, offset) in enumerate(zip(batches, offsets)):
                prog_text.text(f"Classifying batch {b_idx + 1}/{len(batches)} ...")
                try:
                    outs = classifier(batch, LABELS)
                except Exception as e:
                    st.error(f"Classification failed: {e}")
                    outs = []

                for i_local, out in enumerate(outs):
                    global_idx = offset + i_local
                    if not out or "labels" not in out:
                        processed_count += 1
                        prog.progress(processed_count / num)
                        continue

                    label = out["labels"][0]
                    score = out["scores"][0]
                    if score >= CLASSIFY_THRESHOLD and label in LABELS:
                        original_text = to_process[global_idx]
                        headline = original_text.splitlines()[0][:120]
                        results_filtered.append((global_idx, label, headline, original_text))
                    processed_count += 1
                    prog.progress(processed_count / num)

            st.session_state.filtered_articles = results_filtered
            prog_text.text("Classification done. Summarizing positives...")

            # Summarize positives
            summaries = []
            if results_filtered:
                texts_for_summary = [r[3][:MAX_LEN] for r in results_filtered]
                labels_map = [(r[1], r[2]) for r in results_filtered]

                # batch summarization
                sum_batches = [texts_for_summary[i : i + BATCH_SIZE] for i in range(0, len(texts_for_summary), BATCH_SIZE)]
                summed = []
                total_s = len(texts_for_summary)
                done_s = 0
                sum_prog = st.progress(0)
                for sb_idx, sb in enumerate(sum_batches):
                    prog_text.text(f"Summarizing batch {sb_idx + 1}/{len(sum_batches)} ...")
                    try:
                        out_summaries = summarize_batch(sb, min_len=MIN_SUMMARY_LENGTH, max_len=MAX_SUMMARY_LENGTH)
                    except Exception as e:
                        st.warning(f"Summarizer failed for a batch: {e}")
                        out_summaries = [t[:MAX_SUMMARY_LENGTH] for t in sb]

                    for s in out_summaries:
                        summed.append(s)
                        done_s += 1
                        sum_prog.progress(done_s / total_s)

                for (lbl, head), summ in zip(labels_map, summed):
                    summaries.append((lbl, head, summ))

            st.session_state.summaries = summaries
            prog_text.text("Done.")
            st.success(f"Analysis complete — found {len(summaries)} student-related items.")


# ---------------- TAB 2 ----------------
with tab2:
    st.header("Student-Relevant News & Download")
    if not st.session_state.summaries:
        st.info("No analyzed summaries yet. Run analysis in 'Upload & Analyze'.")
    else:
        cols = st.columns([3, 1])
        with cols[0]:
            for i, (tag, head, summ) in enumerate(st.session_state.summaries, 1):
                with st.expander(f"{i}. {head} — [{tag}]"):
                    st.write(summ)
                    st.caption("Original snippet:")
                    try:
                        st.write(st.session_state.filtered_articles[i-1][3][:400] + ("..." if len(st.session_state.filtered_articles[i-1][3]) > 400 else ""))
                    except Exception:
                        st.write(head)
                    st.download_button(f"Download summary {i} (txt)", data=summ, file_name=f"summary_{i}.txt")

        with cols[1]:
            st.metric("Total student items", len(st.session_state.summaries))
            tags = [t for t, _, _ in st.session_state.summaries]
            if tags:
                from collections import Counter
                c = Counter(tags)
                st.subheader("By category")
                for k, v in c.most_common():
                    st.write(f"- {k}: {v}")

            if st.button("Download All as PDF"):
                pdf_bytes = create_pdf_bytes("EduLens - Student Notes", st.session_state.summaries)
                st.download_button("Download compiled PDF", data=pdf_bytes, file_name="EduLens_Student_Notes.pdf")


# ---------------- TAB 3 ----------------
with tab3:
    st.header("About / Help")
    st.markdown(
        """
- If many non-student items are included, raise the classification threshold.
- For faster runs, reduce MAX_BLOCKS or BATCH_SIZE.
- If your PDF is scanned (images), use OCR pipeline externally then paste text here.
"""
    )


# ---------------- TAB 4 ----------------
with tab4:
    st.header("🤖 Ask EduLens AI Assistant")
    user_q = st.text_input("Ask a question (optional)")

    if st.button("Ask"):
        if not openai.api_key:
            st.error("OpenAI API key not set. Set environment variable OPENAI_API_KEY to enable chat.")
        else:
            with st.spinner("Thinking..."):
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant summarizing student-related news."},
                        {"role": "user", "content": user_q},
                    ],
                    max_tokens=300
                )
            st.success(resp["choices"][0]["message"]["content"])
