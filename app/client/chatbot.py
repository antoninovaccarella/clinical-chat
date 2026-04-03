# app.client.chatbot.py
import uuid  # Importing the uuid module for generating unique identifiers

from langchain_core.messages import HumanMessage  # Importing HumanMessage class for representing user messages

from app.rag_agent.workflow import create_workflow  # Importing the create_workflow function to set up the chatbot's workflow


class Chatbot:
    def __init__(self):
        """
        Initializes the Chatbot with configuration and the compiled workflow.
        """
        workflow, memory = create_workflow()  # Create the workflow and memory objects
        self.thread_id = str(uuid.uuid4())  # Generate a unique thread ID using UUID
        print("thread_id = ", self.thread_id)  # Print the generated thread ID for debugging
        self.config = {"configurable": {"thread_id": self.thread_id}}  # Store configuration, including the thread ID
        self.workflow = workflow.compile(checkpointer=memory)  # Compile the workflow with memory for checkpointing

    def process_input(self, user_input):
        """
        Processes the user input by passing it to the workflow and streaming the output.

        Args:
            user_input: The user's input string.

        Returns:
            A dictionary containing the generated response, or a fallback message if no response is generated.
        """
        messages = HumanMessage(content=user_input["question"])  # Create a HumanMessage object from user input
        print(messages)  # Print the HumanMessage object for debugging
        input_message = {"messages": [messages]}  # Prepare the input message for the workflow
        request_config = {
            "configurable": {
                "thread_id": self.thread_id,
                "model_name": user_input.get("model", ""),
                "api_key": user_input.get("api_key", ""),
            }
        }
        # Iterate over the outputs streamed from the workflow
        for output in self.workflow.stream(input_message, request_config):
            # Iterate over key-value pairs in each output
            for key, value in output.items():
                # Extract the generated response if it exists
                generated_response = value.get("messages")
                response = generated_response[-1].content
                if response:
                    return {"response": response}  # Return the generated response

        # If no response is generated, return a fallback message
        return {"response": "I'm sorry, I couldn't process your question."}
