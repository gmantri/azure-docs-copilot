import os

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.schema.messages import HumanMessage

# load environment variables
load_dotenv()

# set path of chroma db
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

# check if Vector database is initialized
if not (os.path.exists(CHROMA_DB_PATH) and os.path.isdir(CHROMA_DB_PATH)):
    print("Vector store not initialized. Please run setup first using \"python3 src/setup.py\".")
    exit()

# read environment variables
AZURE_OPENAI_EMBEDDING_MODEL_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_NAME")
AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME")
AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME")

embedding = OpenAIEmbeddings(deployment=AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME,
                             model=AZURE_OPENAI_EMBEDDING_MODEL_NAME,
                             chunk_size=1)

chroma_db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding)

# setup prompt template
template = """
Use the following pieces of context to answer the question at the end. Question is enclosed in <question></question>.
Do keep the following things in mind when answering the question:
- If you don't know the answer, just say that you don't know, don't try to make up an answer.
- Keep the answer as concise as possible.
- Use only the context to answer the question. Context is enclosed in <context></context>
- The context contains one or more paragraph of text that is formatted as markdown. When answering, 
remove the sentences from the markdown that contain markdown links.
- If the answer is not found in context, simply output "I'm sorry but I do not know the answer to your question. Please visit Microsoft Learn (https://learn.microsoft.com) or ask a question on StackOverflow (https://stackoverflow.com/questions/tagged/azure).
- Do not include the code in output unless the question is asked to produce the code.


<context>{context}</context>
<question>{question}</question>
"""
prompt_template = PromptTemplate.from_template(template)

# initialize LLM
llm = AzureChatOpenAI(deployment_name=AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME, temperature=0)
print("==============================")
print("Welcome to Azure Docs Copilot.")
print("==============================")
while True:
    user_input = input("\n\033[31mAsk a question about Azure and press enter. To terminate, simply type "
                       "\"quit\" and press enter.\033[m\n")
    if user_input.strip() == "":
        print("")
        continue
    if user_input.lower() == "quit":
        print("Thank you for using Azure Docs Copilot.")
        break
    vector_result = chroma_db.similarity_search(query=user_input, search_type="mmr", fetch_k=10)
    context = ""
    for doc in vector_result:
        context += doc.page_content + "\n\n"
    prompt = prompt_template.format(context=context, question=user_input)
    message = HumanMessage(content=prompt)
    result = llm([message])
    print('\033[32m' + result.content + '\033[m')
