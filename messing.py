from flask import Flask, request, jsonify
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_postgres import PostgresChatMessageHistory
from langchain_community.embeddings import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
import psycopg

app = Flask(__name__)

def embedding_text(text, embeddor):
    faiss = FAISS.from_texts(text, embeddor)
    return faiss

def do_similarity_search(query: str, text: list = None, huggingface_model: str = "all-MiniLM-L6-v2"):
    embedding_model = HuggingFaceEmbeddings(model_name=huggingface_model)
    faiss = embedding_text(text, embedding_model)
    result = faiss.similarity_search(query)
    return result

def embedding_similar_history(history_list, query):
    message_list = [message.content for message in history_list if isinstance(message, (AIMessage, HumanMessage))]
    pure_message_list = []
    for document in do_similarity_search(query, message_list):
        pure_message_list.append(document.page_content)
    return pure_message_list 

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/invoke_chat2', methods=['POST'])
def invoke_chat2():
    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id")

    conn_info = "dbname=Chatverse user=postgres password=anshanshansh host=localhost port=5432"
    sync_connection = psycopg.connect(conn_info)

    try:
        chat_history = PostgresChatMessageHistory("chat_history", session_id, sync_connection=sync_connection)
        previous_messages = chat_history.messages
        chat_history.add_message(HumanMessage(content=user_message))
        chat = ChatOllama(model="llama3", verbose=True)
        context_messages = previous_messages + [HumanMessage(content=user_message)]
        ai_response = chat(context_messages)
        chat_history.add_message(AIMessage(content=ai_response.content))
        response_content = {
            "content": ai_response.content,
            "type": ai_response.type,
        }
        return jsonify({"response": response_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        sync_connection.close()

@app.route('/get_messages', methods=['GET'])
def get_messages():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400

    conn_info = "dbname=Chatverse user=postgres password=anshanshansh host=localhost port=5432"
    sync_connection = psycopg.connect(conn_info)

    try:
        chat_history = PostgresChatMessageHistory("chat_history", session_id, sync_connection=sync_connection)
        messages = chat_history.messages
        message_list = [{"type": message.type, "content": message.content} for message in messages]
        return jsonify(message_list), 200
    finally:
        sync_connection.close()

def store_to_vector(history_list):
    embeddor = OllamaEmbeddings(model="llama3")
    vector_store = FAISS()
    for chunk in history_list:
        actual_embeddor = embeddor.embed_query(chunk.content)
        vector_store.add_texts([chunk.content], [actual_embeddor])
    return vector_store

@app.route("/invoke_chat", methods=['POST'])
def invoke_chat():
    data = request.json
    history = data.get('History')

    history_list = []
    if history:
        for chunk in history:
            user_message = chunk.get('User') 
            if not chunk.get('Bot'):
                history_list.append(HumanMessage(content=user_message))
                global last_message 
                last_message = user_message
                break
            bot_message = chunk.get('Bot')
            history_list.append(HumanMessage(content=user_message))
            history_list.append(AIMessage(content=bot_message))
    else:
        return jsonify({"error": "No message or session ID provided"}), 400
    
    try:
        chat = ChatOllama(model="llama3", verbose=True)

        # Perform similarity search on the entire history
        similar_results = embedding_similar_history(history_list, last_message)
        
        # Create the context for the LLM including the most relevant similar results
        context = "\n\n".join(similar_results[:5])  # Adjust the number of results included as needed

        prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Given the following context and conversation history, answer the question, DON'T COUNT TOKENS STRICTLY, just answer the question:"),
        ("assistant", "Context: {context}"),  # Use "assistant" for context
        ("assistant", "Chat History: {chat_history}"),  # Use "assistant" for chat history
        ("human", "{question}"),  # Use "human" for the question
         ])

        prompt = prompt_template.format(
        context=context,
        question=last_message,
        chat_history=history_list  # Using the entire history list as chat history
        )
        ai_response = chat.invoke(prompt)
        history_list.append(AIMessage(content=ai_response.content))

        response_content = {
            "content": ai_response.content,
            "type": ai_response.type,
            "similar_results": "x"
        }
        
        return jsonify({"Response": response_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=2500, debug=True)


