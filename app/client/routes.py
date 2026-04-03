# app.client.routes.py

from flask import Blueprint, request, jsonify  # Import necessary Flask modules
from typing import cast  # For type casting (used for type hinting/checking, not strictly casting at runtime)

from app.client.chatbot import Chatbot  # Import the Chatbot class
from app.client.user_input import UserInput  # Import the UserInput class
from app.rag_agent.clinical_tool.utils import reset_clinical_trials_storage

# Create a Flask Blueprint for the API routes.
# Blueprints help organize routes within a Flask application, especially as the application grows.
# They allow you to group related routes together.
api_blueprint = Blueprint("api", __name__)

# Initialize the Chatbot.
# This creates an instance of the Chatbot class, which handles the core logic of the conversational AI.
chatbot = Chatbot()

# Define the chat route.
# This decorator registers the chat() function as a handler for POST requests to the /chat endpoint.
@api_blueprint.route("/chat", methods=["POST"])
def chat():
    """
    Handles chat requests, receives user input, and returns the chatbot's response.

    This function receives user input (a question) via a POST request to the /chat endpoint,
    passes it to the Chatbot for processing, and then returns the Chatbot's response as a
    JSON object.

    Returns:
        A JSON response containing the chatbot's reply, or an error message if the input is invalid.
    """

    data = request.get_json()  # Get the JSON data from the request

    # Validate the input data.
    # Check if it's a dictionary and contains a "question" key with a string value.
    if not isinstance(data, dict) or "question" not in data or not isinstance(data["question"], str):
        return jsonify({"error": "Invalid input.  'question' must be a string."}), 400  # Return a 400 error if the input is invalid

    if "model" in data and not isinstance(data["model"], str):
        return jsonify({"error": "Invalid input. 'model' must be a string."}), 400

    if "api_key" in data and not isinstance(data["api_key"], str):
        return jsonify({"error": "Invalid input. 'api_key' must be a string."}), 400

    # Type hint the input data as UserInput.
    # This is for static type checking and doesn't perform runtime casting in this case.
    # It helps make the code more readable and less error-prone.
    user_input: UserInput = cast(UserInput, data)  # Type cast the input data to the UserInput type for better type checking
    print("USER_INPUT =", user_input)  # Print the user input for debugging

    # If the user input is "**NEW_CHAT**", re-initialize the chatbot and clear the local trial files.
    # This effectively starts a new conversation.
    if user_input["question"] == "**NEW_CHAT**":
        global chatbot
        chatbot = Chatbot()
        response = {'response': 'New chat!'}
        reset_clinical_trials_storage()
    else:
        response = chatbot.process_input(user_input)  # Process the user input using the chatbot

    # Log the generated response.
    # This is helpful for debugging and monitoring.
    print("RESPONSE FROM CHATBOT (routes):", response)  # Print the chatbot's response for debugging
    return jsonify(response)  # Return the response as a JSON object
