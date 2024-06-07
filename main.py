from flask import Flask, request, jsonify
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_postgres import PostgresChatMessageHistory
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import psycopg

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/invoke_chat2', methods=['POST'])
def invoke_chat2():

    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id")

    
    if not user_message or not session_id:
        return jsonify({"error": "No message or session ID provided"}), 400

    conn_info = "dbname=Chatverse user=postgres password=anshanshansh host=localhost port=5432"
    sync_connection = psycopg.connect(conn_info)

    try:
        # Initialize the chat history manager for the session
        chat_history = PostgresChatMessageHistory("chat_history", session_id, sync_connection=sync_connection)
        
        # Retrieve previous messages
        previous_messages = chat_history.messages
        
        # Add the new user message to the history
        chat_history.add_message(HumanMessage(content=user_message))
        
        # Initialize the chat model
        chat = ChatOllama(model="llama3", verbose=True)
        
        # Create the context for the chat model
        context_messages = previous_messages + [HumanMessage(content=user_message)]
        
        # Get the AI response
        ai_response = chat(context_messages)
        
        # Add the AI response to the message history
        chat_history.add_message(AIMessage(content=ai_response.content))
        
        # Prepare the response content
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
        # Initialize the chat history manager for the session
        chat_history = PostgresChatMessageHistory("chat_history", session_id, sync_connection=sync_connection)
        
        # Retrieve all messages for the session
        messages = chat_history.messages
        
        # Convert the messages to a list of dictionaries for JSON serialization
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


    '''{
  "History": [
    {
      "User": "Hello, how are you?",
      "Bot": "I am good, thank you! How can I assist you today?"
    },
    {
      "User": "Can you tell me a joke?",
      "Bot": "Sure! Why do not scientists trust atoms? Because they make up everything!"
    }
  ]
}'''


    data = request.json


    # user_message = data.get("message")

    history = data.get('History')

    history_list = []

    if history:
        for chunk in history:
            User = chunk.get('User') 
            if(not chunk.get('Bot')):
                history_list.append(HumanMessage(content = User))
                break
            Bot = chunk.get('Bot')
            history_list.append(HumanMessage(content = User))
            history_list.append(AIMessage(content = Bot))

    else:
        return jsonify({"error": "No message or session ID provided"}), 400
    
    try:
        vector_store = store_to_vector(history_list)

        chat = ChatOllama(model="llama3", verbose=True)
        ai_response = chat(history_list)
        history_list.append(AIMessage(ai_response.content))

        response_content = {
                "content": ai_response.content,
                "type": ai_response.type,
            }
        
        return jsonify({"Response": response_content})
        
    except Exception as e:
    
        return jsonify({"error": str(e)}), 500
    
    


    

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
