import os
import sys
import openai
import arabic_reshaper
from bidi.algorithm import get_display
from openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAI as LangChainOpenAI
import warnings

warnings.filterwarnings("ignore")

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = "ما نوع الكتب المتوفؤة في متجرك"

loader = TextLoader("data_ar.txt", encoding="utf-8")
loader.load()

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=openai.api_key)

index = VectorstoreIndexCreator(embedding=embeddings).from_loaders([loader])

llm = LangChainOpenAI(api_key=openai.api_key, temperature=0)

result = index.query(prompt, llm=llm, retriever_kwargs={"search_kwargs": {"k": 1}})

# Reshape and adjust text for proper Arabic display
reshaped_result = arabic_reshaper.reshape(result)
Arabic_result = get_display(reshaped_result)

# Print the properly formatted Arabic text
print(Arabic_result)