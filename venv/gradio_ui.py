import gradio as gr

def handle_user_query(user_input, chatbot_state):
    chatbot_state.append([user_input, None])  # Add user input to the chat state
    return '', chatbot_state

def handle_gemini_response(chatbot):
    chatbot[-1][1] = 'From the function.'
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
        [chatbot],
        [chatbot]
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
