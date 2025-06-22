import json
import os
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluation_chain
from src.mcqgenerator.logger import logging



#import json

with open(r"C:\Users\acer\OneDrive\Desktop\Gen AI\projects\MCQ_generator\Response.json", "r") as file:
    RESPONSE_JSON = json.load(file)



    # Streamlit App
st.title("Quiz Generator App")

with st.form("mcq_form"):
    uploaded_file = st.file_uploader("Upload a PDF or Text file", type=["pdf", "txt"])
    mcq_count = st.number_input("Number of MCQs", min_value=1, max_value=100, step=1, value=5)
    subject = st.text_input("Enter Subject Name", placeholder="e.g., Mathematics, Science")
    tone = st.selectbox("Select Tone", ["Easy", "Medium", "Difficult"])

    button = st.form_submit_button("Generate MCQs")



mcqs = []  # ✅ Ensure `mcqs` is always defined

if button and uploaded_file and mcq_count and subject and tone:
    with st.spinner("Loading.........."):
        try:
            text = read_file(uploaded_file)
            if text:
                with get_openai_callback() as cb:
                    response = generate_evaluation_chain({
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })

                    if response:
                        mcqs = response.get("mcqs", [])  # ✅ Ensure `mcqs` is assigned
                        tokens_used = cb.total_tokens
                        cost = cb.total_cost
                    else:
                        st.error("No response received from the API.")
                        mcqs = []

        except Exception as e:
            st.error(f"An error occurred: {e}")
            logging.error(f"An error occurred: {traceback.format_exc()}")

        else:
            if mcqs:  # ✅ Now `mcqs` is always defined
                st.success("MCQs Generated Successfully! ✅")

                # Display MCQs
                for i, mcq in enumerate(mcqs, 1):
                    st.write(f"**Q{i}:** {mcq['question']}")
                    for choice in mcq["choices"]:
                        st.write(f"- {choice}")
                    st.write(f"✅ **Correct Answer:** {mcq['correct']}")
                    st.write("---")

                # Display API usage details
                st.write("### 📊 API Usage Details")
                st.write(f"**Tokens Used:** {tokens_used}")
                st.write(f"**Estimated Cost:** ${cost:.4f}")
            else:
                st.warning("No MCQs generated. Please check your input and try again.")
