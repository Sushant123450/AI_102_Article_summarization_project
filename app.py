import streamlit as st
import os
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from io import BytesIO
import time

load_dotenv()

openai_key = os.getenv("AZURE_OPENAI_KEY") or ""
openai_api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or ""
openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or ""
form_recognizer_key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
form_recognizer_endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")


if form_recognizer_endpoint and form_recognizer_key:
    document_analysis_client = DocumentAnalysisClient(
        endpoint=form_recognizer_endpoint,
        credential=AzureKeyCredential(form_recognizer_key),
    )

client = AzureOpenAI(
    azure_endpoint=openai_api_endpoint,
    api_key=openai_key,
    api_version="2024-02-01",
)


def extract_text_from_pdf(pdf_file):
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-read", document=pdf_file
    )
    result = poller.result()

    extracted_text = ""
    for page in result.pages:
        for line in page.lines:
            extracted_text += line.content + "\n"

    return extracted_text


def summarize_text(text):
    prompt = f"Summarize the following text in 3 paragraphs:\n{text}."

    response = client.completions.create(
        model=openai_deployment_name,
        prompt=prompt,
        max_tokens=500,  
        temperature=0.7,  
        top_p=0.9, 
        frequency_penalty=0,
        presence_penalty=0,
    )

    summary = response.choices[0].text

    return summary


st.title("PDF/Text Summarizer using Azure AI")

input_type = st.radio("Choose input type", ("Text", "PDF"))

if input_type == "Text":
    user_text = st.text_area("Enter text to summarize")
    if st.button("Summarize Text"):
        if user_text:
            with st.spinner("Summarizing the text..."):
                summary = summarize_text(user_text)
                st.subheader("Summary")
                for paragraph in summary.split("\n"):
                    st.write(paragraph)
                    time.sleep(1)
        else:
            st.warning("Please enter some text.")

elif input_type == "PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_pdf:
        if st.button("Extract and Summarize PDF"):

            pdf_content = BytesIO(uploaded_pdf.read())
            extracted_text = extract_text_from_pdf(pdf_content)
            st.subheader("Extracted Text")
            st.write(extracted_text)

            summary = summarize_text(extracted_text)
            st.subheader("Summary")
            st.write(summary)
