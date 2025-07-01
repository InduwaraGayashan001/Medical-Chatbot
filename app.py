from flask import Flask, render_template, request, jsonify, session
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
import uuid

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

embeddings = download_embeddings()

docsearch = PineconeVectorStore.from_existing_index(
    index_name="medibot",
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

llm = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    base_url="https://models.github.ai/inference",  
    temperature=0.4,
    max_completion_tokens=500
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}"),
])


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Set a random secret key for session management
memory_store = {} 

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    else:
        # Clear memory for current session on reload
        session_id = session['session_id']
        memory_store.pop(session_id, None)
    return render_template('chat.html')


@app.route('/get', methods=['GET', 'POST'])
def chat():
    msg = request.form['msg']
    session_id = session.get('session_id')

    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    memory = memory_store[session_id]

    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    response = rag_chain.invoke({"question": msg})
    return str(response["answer"])

@app.route('/clear', methods=['POST'])
def clear_chat():
    session_id = session.get('session_id')
    if session_id and session_id in memory_store:
        memory_store.pop(session_id)
        print(f"Cleared memory for session_id: {session_id}")
    else:
        print(f"No memory found for session_id: {session_id}")
    return jsonify({"status": "cleared"})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
