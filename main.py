from flask import Flask, request, jsonify
import subprocess
import socket
from langchain_community.chat_models import ChatOllama 
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

app = Flask(__name__)

# Initialize the variable at the global level
ollama_subprocess = None

#@app.route('/start_ollama', methods=['GET'])
def stop_ollama():
    global ollama_subprocess
    if ollama_subprocess is not None:
        ollama_subprocess.terminate()
        ollama_subprocess.wait()
        ollama_subprocess = None
        return
    else:
        return 

def is_port_in_use(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
    
def start_ollama():
    if not is_port_in_use(11434):
       global ollama_subprocess
       # Start Ollama server
       ollama_subprocess = subprocess.Popen(['ollama', 'serve'])

    else:
       return
    
available_ids = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in available_ids:
        available_ids[session_id] = ChatMessageHistory()
    return available_ids[session_id]

           
@app.route('/')
def hello_world():
    return 'Hello, World!'
      
@app.route('/invoke_chat', methods=['POST'])
def invoke_chat():
    #start_ollama()  
    global ollama_subprocess
    # if ollama_subprocess is None or ollama_subprocess.poll() is not None:
    #     return jsonify({"error": "Ollama server is not running"}), 400
    
    
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        config = {"configurable": {"session_id": "abc1"}}
        
        chat = ChatOllama(model="llama3", verbose=True)

        with_message_history = RunnableWithMessageHistory(chat, get_session_history)
        

        ai_response = with_message_history.invoke([HumanMessage(content=user_message)], config=config)
        # Assuming the aim_response is an AIMessage object that needs to be serialized
        # Extract needed data and form a serializable response
        response_content = {
            "content": ai_response.content,
            "type": ai_response.type,
            # Add other fields as necessary
        }
        stop_ollama()
        return jsonify({"response": response_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == "__main__":

    app.run(host="localhost",port=5000, debug=True)
