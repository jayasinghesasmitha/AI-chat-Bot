# Chat Bot with Voice Recognition

## Description
This project is a chat bot that leverages Python, Gradio, and voice recognition to interact with users. The bot can respond to both text and voice inputs, providing a versatile user experience.

## Features
- Chat bot functionality using Python
- Voice recognition for interactive conversations
- User-friendly interface with Gradio
- Support for text and voice inputs

## Technologies Used
- Python
- Gradio
- SpeechRecognition (for voice recognition)

## Installation

### Prerequisites
- Python 3.6 or higher
- OpenAI API key (if applicable for NLP tasks)
- Internet connection

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jayasinghesasmitha/chat-bot-voice-recognition.git
   cd chat-bot-voice-recognition
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (if using OpenAI API):**
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key:
     ```plaintext
     OPENAI_API_KEY=your-api-key-here
     ```

5. **Run the application:**
   ```bash
   cd AI-chat-Bot
   cd Chat bot
   uvicorn run:app --reload
   ```

## Usage
1. Open the Gradio interface by navigating to the provided local URL after running `app.py`.
2. Enter text or use the voice input option to interact with the chat bot.
3. View the chat bot’s responses in real-time.

## Project Structure

```plaintext
├── app.py
├── requirements.txt
├── .env
├── README.md
└── ...
```

## Contributing
Contributions are welcome! Please fork this repository and submit pull requests.

## License
This project is licensed under the MIT License.

## Contact
- **Author:** Sasmitha Jayasinghe
- **Email:** sasmithajayasinghe2002@gmail.com
- **GitHub:** jayasinghesasmitha
