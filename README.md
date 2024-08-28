## What's the Project About?

Chatverse is a powerful chatbot framework designed for handling long-context conversations and advanced session management. It provides several key features:

1. **Long-Context Chatbot**: Chatverse can be used as a chatbot capable of maintaining long-context conversations, making it ideal for complex and interactive dialogues.

2. **Session Management with JSON**: The framework supports robust session management by storing conversation data in JSON format. This allows for easy access and manipulation of session data.

3. **Session Access via JSON Upload**: Users can resume previous sessions by uploading the JSON file generated from earlier conversations, ensuring continuity and context retention.

4. **API Endpoint for No-UI Communication**: Chatverse provides an API endpoint for communication without a user interface, enabling seamless integration with other applications or services.

5. **Token-Based Context Management**: The chatbot implements token-based context management, coupled with long-term memory capabilities, to efficiently handle and recall past interactions.

## How to Use It

To set up and run Chatverse, follow these steps:

1. **Clone the Repository**: This step downloads the Chatverse code to your local machine.

```bash
git clone https://github.com/anshravalll/chatverse.git
cd chatverse
```

2. **Create a Virtual Environment**: Set up a Python virtual environment to isolate the project dependencies from other Python projects on your system.

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install Dependencies**: Install all the necessary Python packages required to run Chatverse. These are listed in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

4. **Run the Flask Server**: Start the Flask server using the provided batch file. This makes the API endpoints available for use.

```bash
run_flask.bat
```

5. **Close the Flask Server**: When you are done using Chatverse, you can stop the server by running the following batch file.

```bash
close_flask.bat
```

6. **Optional: Use the Streamlit UI**: If you prefer to interact with Chatverse through a graphical user interface, run the Streamlit application located in `src/ui.py`.

```bash
streamlit run src/ui.py
```

All API endpoints are defined in `main.py`, with the primary endpoint for invoking the chatbot being `/invoke_chat`. This README serves as the main documentation for setting up and using Chatverse. For more detailed usage instructions, please refer to the comments and examples provided in the codebase.
