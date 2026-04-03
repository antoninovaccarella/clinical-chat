# app.client.user_input.py

from typing import NotRequired, TypedDict  # Import TypedDict for creating typed dictionaries. TypedDict allows you to define the expected structure and types of dictionary data.

class UserInput(TypedDict):
    """
    Typed dictionary representing the structure of user input. This ensures type consistency and helps with code clarity.

    Using TypedDict provides several benefits:
        - Type checking: Tools like MyPy can verify that your code uses the UserInput dictionary correctly, preventing errors related to missing or incorrect data types.
        - Documentation: The TypedDict definition serves as clear documentation of the expected structure of the user input.
        - Code readability:  It makes the code easier to understand by clearly specifying the fields and their types.

    Attributes:
        question: The user's question as a string. This field is required.
    """
    question: str  # The user's question. This field is required because it's part of the TypedDict. It must be a string.
    model: NotRequired[str]
    api_key: NotRequired[str]
