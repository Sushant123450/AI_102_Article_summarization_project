# PDF/Text Summarizer using Azure AI and Streamlit

## Overview

This project is a web application that extracts text from a PDF or processes plain text and summarizes the content using Azure AI's OpenAI GPT model. It uses Streamlit for the UI and Azure Form Recognizer for PDF text extraction.

## Prerequisites

- **Python 3.8+**
- **Azure Subscription** with access to:
  - Azure Form Recognizer
  - Azure OpenAI (with a deployed GPT model)
- **Required Python Libraries**:
  - Streamlit
  - Azure SDK for Form Recognizer and OpenAI
  - Python Dotenv for environment variables
- **API Keys and Endpoints** from Azure OpenAI and Form Recognizer.

---

## Setting Up the Project

### Step 1: Set Up Azure Resources

1. **Azure Form Recognizer**:

   - Go to [Azure Portal](https://portal.azure.com/).
   - Create a new Form Recognizer resource.
   - Copy the **Form Recognizer Key** and **Endpoint**.

2. **Azure OpenAI**:
   - Search for Azure OpenAI in the portal.
   - Create a new resource and deploy a GPT model (e.g., GPT-35-Turbo).
   - Copy the **API Key**, **Endpoint**, and **Deployment Name**.

---

### Step 2: Environment Setup

1. **Clone the Repository** (or set up your project directory):

   ````bash
   git clone https://github.com/your-repo/pdf-text-summarizer.git
   cd pdf-text-summarizer
    ```
   2 . **Install Required Libraries**  Install the required Python libraries using pip
    ```bash
    pip install streamlit azure-ai-formrecognizer azure-openai python-dotenv
    ```
   ````

2. **Create a .env file** in the root directory and add the following keys:
   ```bash
   AZURE_OPENAI_KEY=your-openai-key
   AZURE_OPENAI_ENDPOINT=your-openai-endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   AZURE_FORM_RECOGNIZER_KEY=your-form-recognizer-key
   AZURE_FORM_RECOGNIZER_ENDPOINT=your-form-recognizer-endpoint
   ```

### Step 3: Create the Python Script

Create a Python file (e.g., app.py) in your project directory with the following code:
```python
import streamlit as st
import os
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from io import BytesIO
import time

    # Load environment variables from .env file
    load_dotenv()

    # Azure OpenAI configuration
    openai_key = os.getenv("AZURE_OPENAI_KEY") or ""
    openai_api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or ""
    openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or ""

    # Azure Form Recognizer configuration
    form_recognizer_key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
    form_recognizer_endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")

    # Initialize Document Analysis client
    if form_recognizer_endpoint and form_recognizer_key:
        document_analysis_client = DocumentAnalysisClient(
            endpoint=form_recognizer_endpoint,
            credential=AzureKeyCredential(form_recognizer_key),
        )

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=openai_api_endpoint,
        api_key=openai_key,
        api_version="2024-02-01",
    )

    # Function to extract text from PDF using Azure Form Recognizer
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

    # Function to summarize text using Azure OpenAI
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

    # Streamlit UI
    st.title("PDF/Text Summarizer using Azure AI")

    # Input option: Text or PDF
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
                with st.spinner("Extracting and summarizing the PDF..."):
                    pdf_content = BytesIO(uploaded_pdf.read())
                    extracted_text = extract_text_from_pdf(pdf_content)
                    st.subheader("Extracted Text")
                    st.write(extracted_text)

                    summary = summarize_text(extracted_text)
                    st.subheader("Summary")
                    st.write(summary)
    ```

## Running the Application

1. Start the Streamlit App: In your terminal, navigate to the project directory and run the following command:
   ```bash
   streamlit run app.py
   ```
2. Access the Application: Once Streamlit is running, your web browser will open, or you can go to http://localhost:8501 to view the app.
