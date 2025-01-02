import os
from dotenv import load_dotenv
import gradio as gr
from google.cloud import aiplatform

# Load environment variables from .env file
load_dotenv()

# Set up Google Cloud Vertex AI
project_id = os.getenv("GOOGLE_PROJECT_ID")
location = "us-central1"  # Change as per your region
aiplatform.init(project=project_id, location=location)

# Vertex AI Model and Endpoint
model_name = f"projects/{project_id}/locations/{location}/publishers/google/models/gemini"

def analyze_image(image_path):
    """
    Send an image to Google Gemini and retrieve analysis.
    """
    try:
        endpoint = aiplatform.Endpoint(endpoint_name=model_name)

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Prepare the payload
        instances = [
            {
                "image": {"bytesBase64Encoded": image_bytes.decode("ISO-8859-1")},
                "parameters": {"temperature": 0.5},  # Adjust parameters as needed
            }
        ]

        # Call the Gemini model for image analysis
        response = endpoint.predict(instances=instances)
        return response.predictions[0]["content"]

    except Exception as e:
        return f"Error analyzing image: {e}"

def handle_user_input(user_input, chatbot_state):
    """
    Process user input and add to chatbot history.
    """
    chatbot_state.append([user_input, None])  # Add user's query to the chatbot state
    return "", chatbot_state

def handle_chat_response(chatbot_state, image_path=None):
    """
    Generate a response using Google Gemini, considering uploaded image or text input.
    """
    try:
        last_query = chatbot_state[-1][0]  # Get the latest user query

        # If an image is provided, analyze it
        if image_path:
            image_analysis = analyze_image(image_path)
            chatbot_state[-1][1] = f"Image Analysis:\n{image_analysis}"
        else:
            # Handle text-based queries
            endpoint = aiplatform.Endpoint(endpoint_name=model_name)
            instances = [{"text": last_query, "parameters": {"temperature": 0.5}}]
            response = endpoint.predict(instances=instances)
            chatbot_state[-1][1] = response.predictions[0]["content"]

    except Exception as e:
        chatbot_state[-1][1] = f"Error: {e}"

    return chatbot_state

def reset_chat():
    """
    Reset the chat history and uploaded image.
    """
    return [], None  # Clear chat history and image

# Gradio UI Setup
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center;'>Chat with Gemini AI</h1>")
    gr.Markdown("<p style='text-align: center;'>Upload an image and ask questions about it, or simply chat!</p>")

    chatbot = gr.Chatbot()
    message = gr.Textbox(placeholder="Type your query here...")
    image = gr.Image(type="filepath", label="Upload an Image (optional)")
    clear_button = gr.Button("Reset Chat")

    chatbot_state = gr.State([])  # State to store chatbot history
    uploaded_image = gr.State(None)  # State to store the uploaded image

    # Handle user input
    message.submit(
        handle_user_input, [message, chatbot_state], [message, chatbot]
    ).then(
        handle_chat_response, [chatbot_state, uploaded_image], [chatbot]
    )

    # Handle image upload
    image.upload(lambda img: img, inputs=image, outputs=uploaded_image)

    # Reset chat functionality
    clear_button.click(reset_chat, [], [chatbot, uploaded_image])

    gr.Markdown("<p style='text-align: center;'>Powered by Google Gemini</p>")

if __name__ == "__main__":
    demo.launch()
