import requests  # For making HTTP requests to your Flask app
import json  # For working with JSON data
import os
from telegram import Update  # For handling updates from Telegram
from telegram.ext import (  # For building and managing the Telegram bot
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from app import Config

# Configuration from environment variables
CHATBOT_ENDPOINT = os.getenv("CHATBOT_ENDPOINT", "http://127.0.0.1:5000/chat")
TOKEN = Config.TELEGRAM_API_KEY

# Function to send long messages by splitting them into chunks
async def send_long_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    chunk_size = 4000  # Telegram message limit is 4096, leave some margin
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        await update.message.reply_text(chunk)

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = "**NEW_CHAT**"
    try:
        # Send the user's message to the Flask chatbot endpoint
        response = requests.post(
            CHATBOT_ENDPOINT,
            json={"question": user_message},  # Send message as JSON
            timeout=200000,  # Set a timeout for the request (adjust as needed)
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        bot_response = "Welcome! Ask me anything about Clinical Trials"
    except requests.exceptions.RequestException as e:  # Handle request exceptions
        bot_response = "⚠️ An error occurred while communicating with the service"
        print(f"Error in request to Flask: {str(e)}")  # Print error to console
    except json.JSONDecodeError:  # Handle JSON decoding errors
        bot_response = "⚠️ Error processing the response"
        print("Error parsing JSON response")  # Print error to console
    except Exception as e:  # Handle other exceptions
        bot_response = "⚠️ An unknown error occurred"
        print(f"Generic error: {str(e)}")  # Print error to console
    await update.message.reply_text(bot_response)  # Send welcome message

# Define the /help command handler
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type your question and I will answer.")  # Send help message

# Define the handler for processing text messages (excluding commands)
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text  # Get the user's message

    try:
        # Send the user's message to the Flask chatbot endpoint
        response = requests.post(
            CHATBOT_ENDPOINT,
            json={"question": user_message},  # Send message as JSON
            timeout=2000,  # Set a timeout for the request (adjust as needed)
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        bot_response = response.json().get("response", "No response from the chatbot.") # Extract the response from the JSON

        if len(bot_response) > 4000:  # Check if the message is too long
            await send_long_message(update, context, bot_response)  # Send in chunks
        else:
            await update.message.reply_text(bot_response)  # Send the message as usual

    except requests.exceptions.RequestException as e:  # Handle request exceptions
        bot_response = "⚠️ An error occurred while communicating with the service"
        print(f"Error in request to Flask: {str(e)}")  # Print error to console
    except json.JSONDecodeError:  # Handle JSON decoding errors
        bot_response = "⚠️ Error processing the response"
        print("Error parsing JSON response")  # Print error to console
    except Exception as e:  # Handle other exceptions
        bot_response = "⚠️ An unknown error occurred"
        print(f"Generic error: {str(e)}")  # Print error to console

# Main function to set up and run the bot
def main():
    if not TOKEN:  # Check if the token is configured
        raise ValueError("The Telegram bot token is not configured")

    application = ApplicationBuilder().token(TOKEN).build()  # Create the Application object

    # Register command handlers
    application.add_handler(CommandHandler('start', start))  # Handle /start command
    application.add_handler(CommandHandler('help', help))  # Handle /help command

    # Register message handler for text messages (excluding commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    # Start the bot
    application.run_polling()  # Start polling for updates from Telegram

# Run the main function if the script is executed directly
if __name__ == '__main__':
    main()
