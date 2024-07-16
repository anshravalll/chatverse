from flask import Flask, request, jsonify
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_postgres import PostgresChatMessageHistory
from langchain_community.embeddings import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import psycopg
import tiktoken

app = Flask(__name__)

def token_count(query):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(query)
    return len(tokens)

def split_into_context_boxes(history_list, max_tokens=7000):
    user_tokens = 0
    bot_tokens = 0
    context_box = []
    context_boxes = []
    
    for chunk in history_list:
        if isinstance(chunk, HumanMessage):
            user_tokens += token_count(chunk.content)
        elif isinstance(chunk, AIMessage):
            bot_tokens += token_count(chunk.content)
        
        total_tokens = user_tokens + bot_tokens

        if total_tokens > max_tokens:
            context_boxes.append(context_box)
            context_box = []
            user_tokens = 0
            bot_tokens = 0

        context_box.append(chunk)

    if context_box:
        context_boxes.append(context_box)
    
    return context_boxes

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
        context_boxes = split_into_context_boxes(history_list)
        
        # Use the last context box directly for LLM call
        last_context_box = context_boxes[-1]

        # Perform similarity search on the other context boxes (excluding the last one)
        similar_results = []
        for context_box in reversed(context_boxes[:-1]):
            similar_results.extend(embedding_similar_history(context_box, last_message))
        
        # Create the context for the LLM including the most relevant similar results
        context = "\n\n".join(similar_results[:5])  # Adjust the number of results included as needed

        prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Given the following context and conversation history, answer the question, DON'T COUNT TOKENS STRICTLY your out put must not contain the word token, just answer the question:"),
        ("assistant", "Context: {context}"),  # Use "assistant" for context
        ("assistant", "Chat History: {chat_history}"),  # Use "assistant" for chat history
        ("human", "{question}"),  # Use "human" for the question
         ])

        prompt = prompt_template.format(
        context=context,
        question= last_context_box[-1],
        chat_history=last_context_box
        )
        ai_response = chat.invoke(prompt)
        history_list.append(AIMessage(content=ai_response.content))

        response_content = {
            "content": ai_response.content,
            "type": ai_response.type,
            "similar_results": context
        }
        
        return jsonify({"Response": response_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
