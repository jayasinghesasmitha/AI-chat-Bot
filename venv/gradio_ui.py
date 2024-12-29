import os
import gradio as gr
import google.generativeai as genai
import mysql.connector
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel()

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),  
        user=os.getenv('DB_USER'),  
        password=os.getenv('DB_PASSWORD'),  
        database=os.getenv('DB_NAME') 
    )

# Function to handle queries related to the 'customer' and 'client' tables
def handle_database_query(user_input):
    # Extract the query type from the user input
    query = None
    if "customer" in user_input.lower():
        query = "SELECT * FROM customer"
    elif "client" in user_input.lower():
        query = "SELECT * FROM client"

    if query:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            connection.close()
            # Format the result into a user-friendly string
            formatted_result = "\n".join([f"ID: {row[0]}, Name: {row[1]}, Mobile: {row[2]}" for row in result])
            return formatted_result
        except Exception as e:
            return f"Error querying database: {e}"
    else:
        return "Sorry, I don't understand the query."

def handle_user_query(user_input, chatbot_state):
    chatbot_state.append([user_input, None])  
    return '', chatbot_state

def generate_chatbot(chatbot: list[list[str, str]]) -> list[list[str, str]]:
    formatted_chatbot = []
    if len(chatbot) == 0:
        return formatted_chatbot
    for ch in chatbot:
        formatted_chatbot.append(
            {
                "role": "user",
                "parts": [ch[0]]
            }
        )
        formatted_chatbot.append(
            {
                "role": "model",
                "parts": [ch[1]]
            }
        )
    return formatted_chatbot

def handle_gemini_response(chatbot):
    query = chatbot[-1][0]
    # Check if the query involves database interaction
    if 'customer' in query.lower() or 'client' in query.lower():
        db_response = handle_database_query(query)
        chatbot[-1][1] = db_response
    else:
        # Proceed with the Gemini response
        formatted_chatbot = generate_chatbot(chatbot[:-1])
        chat = model.start_chat(history=formatted_chatbot)
        response = chat.send_message(query)
        chatbot[-1][1] = response.text
    return chatbot

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        label='Chat with Gemini',
        bubble_full_width=False,
    )
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    # Initialize an empty state for the chatbot
    chatbot_state = gr.State(value=[])

    # Submit the user input and update the chatbot
    msg.submit(
        handle_user_query,
        [msg, chatbot_state],
        [msg, chatbot]
    ).then(
        handle_gemini_response,
        [chatbot_state],
        [chatbot]
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
