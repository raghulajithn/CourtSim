# import os
# from crewai import Agent
# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv

# load_dotenv()

# llm = ChatGoogleGenerativeAI(
#     model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.3
# )

# judge_agent = Agent(
#     role="Judge",
#     goal="Analyze arguments from both sides and make a fair judgment.",
#     backstory="An experienced judge who ensures fair trial and provides rulings based on the evidence.",
#     llm=llm,
#     verbose=True,
# )

# opp_agent = Agent(
#     role="Opposing Counsel",
#     goal="Refute weak points in the case and highlight contradictions.",
#     backstory="A sharp opposing counsel looking to challenge every claim with logic and evidence.",
#     llm=llm,
#     verbose=True,
# )


# def get_opponent_response(argument: str, context: str):
#     prompt = (
#         f"Given the lawyer said: {argument}\nUse this context to oppose:\n{context}"
#     )
#     return opp_agent.run(prompt)


# def get_judge_response(history: str, context: str):
#     prompt = f"Use the trial history between lawyer and opposition counsel{history}\nUse context:\n{context}\nProvide a verdict."
#     return judge_agent.run(prompt)

import os
from langchain.schema import SystemMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
)

# Define prompts for each agent role
judge_prompt = PromptTemplate(
    input_variables=["history", "context"],
    template="""You are an experienced judge who ensures fair trial and provides rulings based on evidence.
    Your goal is to analyze arguments from both sides and make a fair judgment.
    
    Trial History: {history}
    Context: {context}
    
    Based on the evidence presented, provide a fair and reasoned verdict.""",
)

opposition_prompt = PromptTemplate(
    input_variables=["argument", "context"],
    template="""You are a sharp opposing counsel looking to challenge every claim with logic and evidence.
    Your goal is to refute weak points in the case and highlight contradictions.
    
    Lawyer's Argument: {argument}
    Context: {context}
    
    Provide a strong counter-argument that challenges the claims with logic and evidence.""",
)

# Create RunnableSequences using the | operator (modern LangChain approach)
judge_chain = judge_prompt | llm | StrOutputParser()
opposition_chain = opposition_prompt | llm | StrOutputParser()


def get_opponent_response(argument: str, context: str):
    """Get response from the opposing counsel agent"""
    return opposition_chain.invoke({"argument": argument, "context": context})


def get_judge_response(history: str, context: str):
    """Get response from the judge agent"""
    return judge_chain.invoke({"history": history, "context": context})
