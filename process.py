from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os

DB_FAISS_PATH = "vectorstores/db_faiss"
CHAT_HISTORY_FILE = "chat_history.json"

custom_promt_template = """ Use the following pieces of information to answer the users's question.
IF you don't know the answer, please just say that you don't know the answer, don't try to make up an answer 

Context:{context}
Question:{question}

Only returns the helpful answer below and nothing else.
Helpful answer: 
"""

chat_history = []


def set_custom_prompt():
    prompt = PromptTemplate(
        template=custom_promt_template, input_variables=["context", "question"]
    )
    return prompt

def load_llm():
    MAX_TOKENS = 2048
    llm = OllamaLLM(model="llama3.2", max_tokens=MAX_TOKENS, temperature=0.5)
    return llm

def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return qa_chain

def qa_bot():
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = load_llm()
    qa_prompt = set_custom_prompt()  # phong cách nói
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    return qa

def final_result(query):
    qa_result = qa_bot()
    response = qa_result({"query": query})

    # Append question and answer to chat history
    chat_history.append({"question": query, "answer": response["result"]})

    # Save chat history to file
    save_chat_history()

    return response

def save_chat_history():
    # Store history to JSON file
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_history, f, indent=4)

def load_chat_history():
    # Load history from JSON file
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

chat_history = load_chat_history()

app = FastAPI()

class QueryModel(BaseModel):
    query: str

@app.post("/get-answer")
async def get_answer(query: QueryModel):
    response = final_result(query.query)
    return {"answer": response["result"], "history": chat_history}

@app.get("/get-chat-history")
async def get_chat_history():
    
    return {"history": load_chat_history()}

@app.get("/")
async def read_root():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":   
    uvicorn.run(app, port=8000)
