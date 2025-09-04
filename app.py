import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import docx
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from gtts import gTTS
import speech_recognition as sr
import tempfile
import os

# ------------------ ERIK v7 ------------------
st.set_page_config(page_title="ERIK v7 - AI Academic Assistant", layout="wide")

st.title("🧠 ERIK v7 - Exceptional Resources & Intelligence Kernel")
st.markdown("Created by **Sabid Uddin Nahian** 🚀 | Multilingual AI Assistant with Voice & Audiobook Support")

# ------------------ Sidebar ------------------
st.sidebar.header("Features")
mode = st.sidebar.radio("Choose a feature:", [
    "Ask Question", "Quiz Generator", "PDF/Text Analyzer", "Google Scholar Search", "2D & 3D Graph Generator", "Voice Assistant"
])

# ------------------ Language Detection ------------------
def detect_language(text):
    if any('\u0980' <= ch <= '\u09FF' for ch in text):  # Bangla Unicode
        return "bn"
    elif any('\u4e00' <= ch <= '\u9fff' for ch in text):  # Mandarin
        return "zh-CN"
    elif any('\u00C0' <= ch <= '\u024F' for ch in text):  # German accents
        return "de"
    else:
        return "en"

# ------------------ Summarize Answer ------------------
def summarize_text(text, mode="short"):
    words = text.split()
    if mode == "short":
        return " ".join(words[:50])
    else:
        return " ".join(words[:200])

# ------------------ Ask Question ------------------
if mode == "Ask Question":
    query = st.text_input("Ask your question:")
    answer_mode = st.radio("Answer Format:", ["Short (~50 words)", "Long (~200 words)"])
    if st.button("Search & Answer"):
        st.info("Searching the web... ⏳")
        lang_code = detect_language(query)
        results = []
        try:
            for url in search(query, num_results=5, lang=lang_code):
                results.append(url)
        except:
            st.error("❌ Error searching Google.")
        
        answer = ""
        for link in results:
            try:
                r = requests.get(link, timeout=3)
                soup = BeautifulSoup(r.text, 'html.parser')
                paragraphs = soup.find_all('p')
                for p in paragraphs[:2]:
                    answer += p.get_text() + " "
            except:
                continue
        
        if answer:
            length = "short" if answer_mode.startswith("Short") else "long"
            response = summarize_text(answer.strip(), length)
            st.markdown("💡 **Here’s what I found for you:**")
            st.write(response)
            st.markdown("🔗 **Top sources:**")
            for r in results:
                st.write(f"- {r}")
        else:
            st.warning("⚠️ No relevant answer found.")

# ------------------ PDF/Text Analyzer ------------------
elif mode == "PDF/Text Analyzer":
    uploaded_file = st.file_uploader("Choose a file", type=['pdf','docx','txt'])
    if uploaded_file:
        text = ""
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = str(uploaded_file.read(), "utf-8")
        
        st.text_area("Extracted Text", text, height=300)

        if st.button("Convert to Audiobook 🎧"):
            tts = gTTS(text=text, lang="en")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)

            st.audio(temp_file.name)
            with open(temp_file.name, "rb") as file:
                st.download_button(
                    label="⬇️ Download Audiobook",
                    data=file,
                    file_name="audiobook.mp3",
                    mime="audio/mpeg"
                )

# ------------------ Google Scholar Search ------------------
elif mode == "Google Scholar Search":
    st.subheader("🔬 Google Scholar Search")
    keyword = st.text_input("Enter research topic:")
    if st.button("Search Scholar 🔍"):
        st.info("Fetching top research papers... ⏳")
        query = f"{keyword} site:scholar.google.com"
        results = []
        try:
            for url in search(query, num_results=5):
                results.append(url)
        except:
            st.error("❌ Error searching Scholar.")

        if results:
            st.success(f"Found {len(results)} papers:")
            for r in results:
                try:
                    r_page = requests.get(r, timeout=3)
                    soup = BeautifulSoup(r_page.text, "html.parser")
                    title = soup.title.string if soup.title else r
                    abstract = " ".join([p.get_text()[:200]+"..." for p in soup.find_all('p')[:1]])
                    st.markdown(f"📄 **{title}**\n{abstract}\n🔗 [Read More]({r})")
                except:
                    st.markdown(f"📄 {r}")
        else:
            st.warning("⚠️ No papers found. Try another keyword.")

# ------------------ 2D & 3D Graph Generator ------------------
elif mode == "2D & 3D Graph Generator":
    func_input = st.text_input("Enter function in x (e.g., x**2 + 2*x - 3):")
    graph_type = st.radio("Graph Type:", ["2D", "3D"])
    if st.button("Plot Graph"):
        x = sp.symbols('x')
        try:
            func = sp.sympify(func_input)
            if graph_type == "2D":
                x_vals = np.linspace(-10, 10, 400)
                y_vals = [func.subs(x, val) for val in x_vals]
                plt.plot(x_vals, y_vals)
                plt.xlabel("x")
                plt.ylabel("y")
                st.pyplot(plt)
            else:
                from mpl_toolkits.mplot3d import Axes3D
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                X = np.linspace(-5, 5, 100)
                Y = np.linspace(-5, 5, 100)
                X, Y = np.meshgrid(X, Y)
                Z = np.array([[func.subs({x: X[i][j]}) for j in range(100)] for i in range(100)])
                ax.plot_surface(X, Y, Z, cmap="viridis")
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error plotting graph: {e}")

# ------------------ Voice Assistant ------------------
elif mode == "Voice Assistant":
    st.subheader("🎤 Voice Assistant")
    if st.button("Start Listening"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            st.info("Listening... Speak now 🎙️")
            audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            st.success(f"You said: {query}")
            lang_code = detect_language(query)
            
            # Search & respond
            results = []
            for url in search(query, num_results=3, lang=lang_code):
                results.append(url)
            answer = ""
            for link in results:
                try:
                    r = requests.get(link, timeout=3)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    p = soup.find('p')
                    if p:
                        answer = p.get_text()
                        break
                except:
                    continue
            if answer:
                st.write(answer)
                tts = gTTS(text=answer, lang=lang_code)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(temp_file.name)
                st.audio(temp_file.name)
        except Exception as e:
            st.error(f"Error: {e}")
