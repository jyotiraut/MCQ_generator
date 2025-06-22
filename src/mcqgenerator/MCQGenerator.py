import os 
import json
import pandas as pd 
import traceback
#from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

load_dotenv()

from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file,get_table_data

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
#from langchain.callbacks import get_openai_callback
import PyPDF2
from langchain_community.callbacks.manager import get_openai_callback


key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=key,model_name="gpt-4o",temperature=0.7)


Tempalte ="""
 Text:{text}
 You are an expert MCQ Generator. Given the above text,it is your job to \
 create a quiz of{number} multiple choice questions for the {subject}
 in {tone} tone. 
 Make sure the questions are not repeated and check all the question conforming 
 the text as well.
 Make sure to format your response like RESPONSE_JSON below and use it as a guide.\
 Ensure to make the {number} MCQs
 ###RESPONSE_JSON
 {response_json}



"""

quiz_generation_pronmpt = PromptTemplate(
    input_variables=["text","number","subject","tone","response_json"],
    template=Tempalte
)

quiz_chain = LLMChain(llm=llm,prompt=quiz_generation_pronmpt,output_key="quiz",verbose=True)


Tempalte2 = """You are an expert english grammarian and writer.Given a Multiple Choice Quiz for{subject} students.\
    You nedd to evaluate the complexity of the questions and give a complete analysis of the quiz. Only use at max 50 words for complexity
    if the quiz is not as per with the cognitive and analytical abilities of the students,\
    update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student.\
        Quiz_MCQs:
        {quiz}
        check from an expert English writer of the above quiz:
        """

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject","quiz"],
    template=Tempalte2
)

review_chain = LLMChain(llm=llm,prompt=quiz_evaluation_prompt,output_key="review",verbose=True)

generate_evaluation_chain = SequentialChain(chains=[quiz_chain,review_chain],input_variables=["text","number","subject","tone","response_json"],output_variables=["quiz","review"],verbose=True)

