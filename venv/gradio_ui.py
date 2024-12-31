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
    if 'customer' in query.lower() or 'client' in query.lower():
        db_response = handle_database_query(query)
        chatbot[-1][1] = db_response
    else:
        formatted_chatbot = generate_chatbot(chatbot[:-1])
        chat = model.start_chat(history=formatted_chatbot)
        response = chat.send_message(query)
        chatbot[-1][1] = response.text
    return chatbot

# Function to reset the chatbot
def reset_chat():
    return []

# Main Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align:center;'>Chat with database</h1>")
    gr.Markdown("<p style='text-align:center;'>An interactive chatbot to help you with database queries and general questions!</p>")

    chatbot = gr.Chatbot(
        label='Chat with Gemini',
        show_label=True,
        avatar_images=("https://img.icons8.com/fluency/48/chatbot.png", "https://img.icons8.com/color/48/user-male-circle.png"),
        bubble_full_width=False,
    )
    msg = gr.Textbox(
        label="Your Query",
        placeholder="Type a question here...",
        lines=1,
        max_lines=2
    )
    clear = gr.ClearButton([msg, chatbot], value="Reset Chat")

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

    gr.Examples(
        examples=[
            "Show all customers",
            "Show all clients",
            "What is AI?",
            "What is database?"
        ],
        inputs=msg,
    )

    gr.Markdown("<p style='text-align:center;'>Powered by <b>Google Gemini</b> and <b>MySQL</b></p>")

if __name__ == "__main__":
    demo.queue()
    demo.launch()
