# app.rag_agent.workflow.py

# Import necessary modules from langchain-core for handling AI messages.
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

# Import MemorySaver from langgraph for saving and loading workflow state.
from langgraph.checkpoint.memory import MemorySaver

# Import essential components from langgraph for defining the workflow graph.
from langgraph.graph import END, StateGraph, START, MessagesState

# Import the get_react_agent_response function from the react_agent module.
from app.rag_agent.react_agent import get_react_agent_response


def generate_response(state, config: RunnableConfig):
    """
    Generate a response using the React-based agent.

    Args:
        state: The current state of the workflow, containing messages.

    Returns:
        dict: Updated state with the new AI response added to the messages.
    """
    print("---generate_react---")  # Debugging: Print a message indicating the function execution.
    messages = state["messages"]  # Extract the list of messages from the current state.
    print("messages = ", messages)  # Debugging: Print the extracted messages.
    configurable = config.get("configurable", {})
    response_text = get_react_agent_response(
        messages,
        model_name=configurable.get("model_name", ""),
        api_key=configurable.get("api_key", ""),
    )  # Call the get_react_agent_response function to generate a response.
    print(
        "---generate_response--- response_text = ", response_text
    )  # Debugging: Print the generated response.
    ai_response = AIMessage(
        content=response_text
    )  # Create an AIMessage object from the response text.
    messages.append(
        ai_response
    )  # Add the new AI message to the list of messages.
    return {"messages": messages}  # Return the updated state with the new messages.


def create_workflow():
    """
    Create and configure the state graph workflow.

    This function initializes a workflow graph using MessagesState as the schema.
    It sets up a node for generating responses and defines the execution flow
    from START to END.

    Returns:
        tuple: A tuple containing the configured workflow and memory saver.
    """
    workflow = StateGraph(
        state_schema=MessagesState
    )  # Initialize a state graph with MessagesState schema.
    workflow.add_node(
        "generate_response", generate_response
    )  # Add a node named 'generate_response' that executes the generate_response function.
    workflow.add_edge(
        START, "generate_response"
    )  # Connect the START node to the 'generate_response' node.
    workflow.add_edge(
        "generate_response", END
    )  # Connect the 'generate_response' node to the END node.
    memory = MemorySaver()  # Create a MemorySaver instance for saving workflow states.
    return workflow, memory  # Return the workflow and memory saver.
