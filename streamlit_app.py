import streamlit as st
import openai
from docx import Document
import fitz  # PyMuPDF for PDF reading
import os
from dotenv import load_dotenv

# Set page to wide mode for more space
st.set_page_config(layout="wide")

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Please set your OPENAI_API_KEY in the .env file")
    st.stop()

def extract_text(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    else:
        return "Unsupported file type."

def translate_with_gpt(text):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Translate French text to English. Preserve structure and formatting."},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

st.title("📄 French-to-English Translator (GPT-4)")

# Add tabs for different input methods
tab1, tab2 = st.tabs(["📝 Text Input", "📂 File Upload"])

french_text = ""

with tab1:
    french_text = st.text_area("Enter French text to translate:", height=200)

with tab2:
    uploaded_file = st.file_uploader("Upload a French document", type=["txt", "docx", "pdf"])
    if uploaded_file:
        french_text = extract_text(uploaded_file)

if french_text:
    with st.spinner("Translating with GPT-4..."):
        english_text = translate_with_gpt(french_text)

    # Create wider columns
    col1, col2 = st.columns([1, 1])  # Equal width columns

    with col1:
        st.subheader("📘 French")
        st.text_area("Original Text", french_text, height=400, key="french")

    with col2:
        st.subheader("📙 English (GPT-4)")
        st.text_area("Translation", english_text, height=400, key="english")

    st.download_button("Download Translation", english_text, file_name="translation.txt")
