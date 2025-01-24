import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# Configure API key (**Important:** Do NOT hardcode API keys directly in your code)
# Consider using environment variables or a secure secrets management solution.
# genai.configure(api_key='YOUR_API_KEY') 

# Create GenerativeModel instance
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Streamlit app
st.title('ServiceNow Tickets PDF Assistant')

# Option to load PDF from local path
local_pdf_path = st.text_input("Enter the local path to the PDF:")

# Button to trigger PDF loading
load_button = st.button("Load PDF")

pdf_content = None 

if load_button and local_pdf_path:
    try:
        pdf_reader = PdfReader(local_pdf_path)
        descriptions = []
        resolutions = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            description_start = page_text.find("Short Description:")
            if description_start != -1:
                description_start += len("Short Description:")
                description_end = page_text.find("Resolution:")
                descriptions.append(page_text[description_start:description_end].strip())

            resolution_start = page_text.find("Resolution:")
            if resolution_start != -1:
                resolution_start += len("Resolution:")
                resolutions.append(page_text[resolution_start:].strip())

        pdf_content = {"descriptions": descriptions, "resolutions": resolutions}
    except FileNotFoundError as e:
        st.error(f"File not found at the specified path: {e}")
    except Exception as e:
        st.error(f"An error occurred while loading the PDF: {e}")

# User input for questions
user_input = st.text_input("Ask a question about the PDF:")
submit_button = st.button("Submit")

if submit_button and user_input:
    # Construct a refined prompt
    if pdf_content:
        prompt = f"""
        **Question:** {user_input}

        **Context:** 
        This PDF contains information about Service Now tickets, including "Short Description" and "Resolution" for each ticket.

        **Instructions:**
        1. If the question can be answered directly from the "Short Description" of any ticket, answer based on that.
        2. If the question requires information from the "Resolution" of any ticket to be answered correctly, use the "Resolution" information.
        3. If the answer cannot be found in either "Short Description" or "Resolution", state "Answer not found in the provided PDF."

        **Data:**
        * **Short Descriptions:** {pdf_content["descriptions"]}
        * **Resolutions:** {pdf_content["resolutions"]}

        Answer the question concisely and accurately based on the provided data and instructions.
        """

        # Generate answer using the Gemini model
        response = model.generate_content(contents=[prompt])
        st.write(f"MES Bot: {response.text}")
    else:
        st.warning("Please load a PDF file first.")