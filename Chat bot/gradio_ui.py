import os
import gradio as gr
import google.generativeai as genai
import mysql.connector
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
from dotenv import load_dotenv, find_dotenv

# Load environment variables
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

# Handle user query
def handle_user_query(user_input, chatbot_state, chat_history):
    chatbot_state.append([user_input, None])
    return '', chatbot_state, chat_history

# Generate chatbot messages
def generate_chatbot(chatbot):
    formatted_chatbot = []
    for ch in chatbot:
        formatted_chatbot.append(
            {"role": "user", "parts": [ch[0]]}
        )
        if ch[1]:
            formatted_chatbot.append(
                {"role": "model", "parts": [ch[1]]}
            )
    return formatted_chatbot

# Handle Gemini response
def handle_gemini_response(chatbot, chat_history):
    query = chatbot[-1][0]
    if 'customer' in query.lower() or 'client' in query.lower():
        db_response = handle_database_query(query)
        chatbot[-1][1] = db_response
    else:
        formatted_chatbot = generate_chatbot(chatbot[:-1])
        chat = model.start_chat(history=formatted_chatbot)
        response = chat.send_message(query)
        chatbot[-1][1] = response.text
    chat_history.append(chatbot[-1])  
    return chatbot, chat_history

# Voice-to-text function
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now. ")
            
            print("Recording... Please speak.")
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=6) 

            # Process the audio and recognize speech
            print("Processing your input...")
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand your speech. Could you try again?"
        except sr.RequestError as e:
            return f"Sorry, there was an issue with the speech recognition service: {e}"
        except Exception as e:
            return f"An error occurred: {e}"

# Text-to-voice function
def text_to_speech(text):
    tts = gTTS(text)
    tts.save("response.mp3")
    audio = AudioSegment.from_file("response.mp3", format="mp3")
    play(audio)
    os.remove("response.mp3")

# Function to reset the chatbot (keep history intact)
def reset_chat_with_history(chat_history):
    return [], [], chat_history  

# View chat history
def view_chat_history(chat_history):
    return "\n".join(
        [f"User: {msg[0]}\nBot: {msg[1]}" for msg in chat_history if msg[1] is not None]
    )

# Main Gradio interface
with gr.Blocks(css="""
    body {
        font-family: 'Poppins', sans-serif; /* Stylish font */
        background: linear-gradient(135deg, #74ebd5, #ACB6E5); /* Attractive gradient */
        color: #333333; 
    }
    .gradio-container {
        font-family: 'Poppins', sans-serif;
    }
    .gr-button {
        background: linear-gradient(45deg, #6A11CB, #2575FC);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        padding: 12px 20px;
        cursor: pointer;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
    }
    .gr-button:active {
        transform: scale(0.95);
    }
""") as demo:
    gr.Markdown("<h1 style='text-align:center; color:white;'>✨ AI chatbot ✨</h1>")
    gr.Markdown("<p style='text-align:center; color:white;'>Chat, speak, or review your chat history with ease!</p>")

    chatbot = gr.Chatbot(
        label='Chat with AI Chatbot',
        bubble_full_width=False
    )
    msg = gr.Textbox(
        label="Your Query",
        placeholder="Type your question or use the mic...",
        lines=1,
        max_lines=2
    )

    with gr.Row():
        record_button = gr.Button("🎤 Record Voice")
        reset_button = gr.Button("🔄 Reset Chat")
        view_history_button = gr.Button("📜 View History")

    view_history_output = gr.Textbox(
        label="Chat History",
        placeholder="Chat history will appear here...",
        lines=10,
        interactive=False,
        visible=False
    )

    chatbot_state = gr.State(value=[])
    chat_history = gr.State(value=[])

    # Submit the user input and update the chatbot
    msg.submit(
        handle_user_query,
        [msg, chatbot_state, chat_history],
        [msg, chatbot, chat_history]
    ).then(
        handle_gemini_response,
        [chatbot_state, chat_history],
        [chatbot, chat_history]
    )

    # Record voice and transcribe
    record_button.click(
        record_and_transcribe,
        outputs=msg
    )

    # Reset chat but keep history
    reset_button.click(
        reset_chat_with_history,
        inputs=[chat_history],
        outputs=[chatbot, chatbot_state, chat_history]
    )

    # View chat history
    view_history_button.click(
        view_chat_history,
        inputs=[chat_history],
        outputs=[view_history_output]
    ).then(
        lambda: gr.update(visible=True),
        outputs=[view_history_output]
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch(share=True)
