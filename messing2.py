from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

model = ChatOllama(model="llama3")
parser = JsonOutputParser()
format_instructions = parser.get_format_instructions()
prompt_template = f"""
You are a home automation JSON creator, which understands the sentiments of the user and creates a file in json format which contains different fields related to home automation actions.
{format_instructions}
query:{{query}}
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["query"])

chain = prompt | model | parser 

for chunk in chain.stream({"query": "turn air conditioner to 24"}):
    print(chunk, end="\n")
