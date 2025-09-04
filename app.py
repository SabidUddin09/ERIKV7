import streamlit as st
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import docx
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import io
import random
import speech_recognition as sr
from gtts import gTTS
import edge_tts
import asyncio
import tempfile
import os
import base64

# ------------------ ERIK v7.1 ------------------
st.set_page_config(page_title="ERIK v7.1 - AI Academic Assistant", layout="wide")

st.title("🧠 ERIK v7.1 - Exceptional Resources & Intelligence Kernel")
st.markdown("Created by **Sabid Uddin Nahian** 🚀 | Multilingual AI Assistant with Voice & Audiobook Support")

# ------------------ Sidebar ------------------
st.sidebar.header("Features")
mode = st.sidebar.radio("Choose a feature:", [
    "Ask Question",
    "Quiz Generator",
    "PDF/Text Analyzer",
    "Google Scholar Search",
    "2D & 3D Graph Generator"
])

# Helper: Audio Player
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# ------------------ Language Detection (Simple Rule) ------------------
def detect_language(text):
    if any('\u0980' <= ch <= '\u09FF' for ch in text):
        return "bn"  # Bangla
    elif any('\u4e00' <= ch <= '\u9fff' for ch in text):
        return "zh"  # Chinese (Mandarin)
    elif any('\u00C0' <= ch <= '\u024F' for ch in text):
        return "de"  # German-ish
    else:
        return "en"  # Default English

# ------------------ Humanoid Response ------------------
def generate_response(query, mode="short"):
    lang = detect_language(query)
    if mode == "short":
        length = 50
    else:
        length = 200
    # Simple rule-based offline response engine
    base_resp = f"This is a {mode} answer ({length} words approx) for your question: {query}"
    if lang == "bn":
        base_resp = f"এটি একটি {mode} উত্তর (প্রায় {length} শব্দ) আপনার প্রশ্নের জন্য: {query}"
    elif lang == "de":
        base_resp = f"Dies ist eine {mode} Antwort (ca. {length} Wörter) auf Ihre Frage: {query}"
    elif lang == "zh":
        base_resp = f"这是一个{mode}答案（大约{length}个字）关于你的问题: {query}"
    return base_resp

# ------------------ Ask Question ------------------
if mode == "Ask Question":
    st.subheader("Ask anything (Text or Voice)")

    query = st.text_input("Type your question:")
    voice_input = st.button("🎤 Speak your question")

    if voice_input:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... speak now!")
            audio = recognizer.listen(source, phrase_time_limit=5)
        try:
            query = recognizer.recognize_google(audio)
            st.success(f"Recognized: {query}")
        except:
            st.error("Sorry, could not recognize your voice.")

    ans_type = st.radio("Answer length:", ["Short (~50 words)", "Long (~200 words)"])

    if st.button("Get Answer"):
        if query:
            mode_choice = "short" if "Short" in ans_type else "long"
            response = generate_response(query, mode=mode_choice)
            st.write(response)

            # Voice Response
            tts_choice = st.selectbox("Choose AI Voice:", ["gTTS - Default", "Edge-TTS - Male", "Edge-TTS - Female"])
            if tts_choice.startswith("gTTS"):
                tts = gTTS(text=response, lang=detect_language(query))
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp.name)
                autoplay_audio(tmp.name)
            else:
                voice = "en-US-GuyNeural" if "Male" in tts_choice else "en-US-JennyNeural"
                async def _speak():
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    communicate = edge_tts.Communicate(response, voice)
                    await communicate.save(tmp.name)
                    return tmp.name
                path = asyncio.run(_speak())
                autoplay_audio(path)
        else:
            st.warning("Please enter or speak a question.")

# ------------------ Quiz Generator ------------------
elif mode == "Quiz Generator":
    st.subheader("Generate Quizzes")
    topic = st.text_input("Enter topic for quiz:")
    num_q = st.number_input("Number of questions:", 1, 10, 3)
    if st.button("Generate Quiz"):
        for i in range(num_q):
            st.write(f"Q{i+1}: Placeholder question on {topic}?")
            st.write("a) Option A  b) Option B  c) Option C  d) Option D")
            st.write("Answer: Option A")

# ------------------ PDF/Text Analyzer ------------------
elif mode == "PDF/Text Analyzer":
    st.subheader("Upload PDF/DOCX/TXT and Convert to Audiobook")
    uploaded = st.file_uploader("Choose a file", type=['pdf','docx','txt'])
    if uploaded:
        text = ""
        if uploaded.type == "application/pdf":
            doc = fitz.open(stream=uploaded.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
        elif uploaded.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = str(uploaded.read(), "utf-8")

        st.text_area("Extracted Text", text, height=300)

        if st.button("Convert to Audiobook"):
            voice_opt = st.selectbox("Choose Voice:", [
                "gTTS - Default",
                "Edge-TTS - Female (English US)",
                "Edge-TTS - Male (English UK)",
                "Edge-TTS - Female (Bangla)",
                "Edge-TTS - Male (German)"
            ])
            if voice_opt.startswith("gTTS"):
                tts = gTTS(text=text[:5000], lang="en")
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp.name)
                autoplay_audio(tmp.name)
            else:
                voices = {
                    "Edge-TTS - Female (English US)": "en-US-JennyNeural",
                    "Edge-TTS - Male (English UK)": "en-GB-RyanNeural",
                    "Edge-TTS - Female (Bangla)": "bn-BD-NabanitaNeural",
                    "Edge-TTS - Male (German)": "de-DE-ConradNeural"
                }
                async def _speak():
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    communicate = edge_tts.Communicate(text[:5000], voices[voice_opt])
                    await communicate.save(tmp.name)
                    return tmp.name
                path = asyncio.run(_speak())
                autoplay_audio(path)

# ------------------ Google Scholar Search ------------------
elif mode == "Google Scholar Search":
    st.subheader("Search Google Scholar")
    query = st.text_input("Enter research topic:")
    if st.button("Search Scholar"):
        search_url = f"https://scholar.google.com/scholar?q={query}"
        try:
            r = requests.get(search_url, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.select('.gs_ri')
            for res in results[:5]:
                title = res.select_one('.gs_rt').get_text() if res.select_one('.gs_rt') else "No title"
                abstract = res.select_one('.gs_rs').get_text() if res.select_one('.gs_rs') else "No abstract"
                link = res.select_one('.gs_rt a')['href'] if res.select_one('.gs_rt a') else "#"
                st.markdown(f"**[{title}]({link})**\n\n{abstract}\n")
        except:
            st.error("Error fetching results. Scholar may have blocked the request.")

# ------------------ Graph Generator ------------------
elif mode == "2D & 3D Graph Generator":
    st.subheader("Graph Generator")
    expr = st.text_input("Enter function f(x):", "x**2")
    graph_type = st.radio("Graph type:", ["2D", "3D"])
    if st.button("Plot"):
        x = sp.symbols('x')
        f = sp.sympify(expr)
        x_vals = np.linspace(-10, 10, 400)
        y_vals = [f.subs(x, val) for val in x_vals]

        if graph_type == "2D":
            plt.figure()
            plt.plot(x_vals, y_vals)
            plt.title(f"Graph of {expr}")
            st.pyplot(plt)
        else:
            from mpl_toolkits.mplot3d import Axes3D
            X = np.linspace(-5, 5, 50)
            Y = np.linspace(-5, 5, 50)
            X, Y = np.meshgrid(X, Y)
            Z = [[f.subs({x: xx}) for xx in row] for row in X]
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(X, Y, Z)
            st.pyplot(fig)
