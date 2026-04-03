# app.rag_agent.react_agent.py

# Import necessary modules from LangChain and other libraries
from langchain import hub  # For integrating LangChain's hub
from langchain.agents import AgentExecutor, create_react_agent  # For creating and managing ReAct agents
from langchain_community.tools import PubmedQueryRun  # Tool for querying PubMed articles
from langchain_core.prompts import PromptTemplate  # Template for formatting the prompt
from langchain_core.tools import Tool  # Generic tool interface
from langchain_experimental.utilities import PythonREPL  # REPL (Read-Eval-Print Loop) for executing Python code

# Import custom modules
from app.large_language_models import get_chat_model
from app.rag_agent.clinical_tool.clinical_trials_search_tool import ClinicalSearchTool  # Clinical trials search tool


def get_react_agent_response(question: dict, model_name: str = "", api_key: str = "") -> str:
    """
    Generates a response using a ReAct-based agent with multiple tools.

    Parameters:
    question (list): A list containing the query text.

    Returns:
    list: The generated response from the agent.
    """
    try:
        # Initialize the Large Language Model (LLM)
        llm = get_chat_model(model_name=model_name, api_key=api_key)

        # Initialize a Python REPL tool for executing Python commands
        python_repl = PythonREPL()
        python_repl_ast = Tool(
            name="python_repl_ast",
            description="A Python shell. Use this to execute Python commands. Input should be a valid Python command. If you want to see the output of a value, you should print it out with `print(...)`.",
            func=python_repl.run,
        )

        # Initialize external tools
        clinical_tool = ClinicalSearchTool(selected_model=model_name, api_key=api_key)  # Clinical trials search tool
        pubmed_tool = PubmedQueryRun()  # PubMed query tool for retrieving medical literature

        # List of available tools
        tools = [clinical_tool, python_repl_ast, pubmed_tool]

        # Define the agent's task and guidelines for tool usage
        agent_task="""TASK:

You are a helpful assistant designed to answer questions in the clinical and medical domain.

You will receive a wide range of queries, which may include:
- Simple questions (e.g., general knowledge, greetings, and conversational topics).
- Questions related to clinical trials (i.e., queries requiring to download clinical trials from ClinicalTrials.gov to search for an answer).
- Questions related to the medical domain (i.e., queries that should be supported by published literature, such as works available in PubMed).

Provide clear, detailed, and well-structured responses to user inquiries, including as much relevant information as possible.  
      
You have access to the following tools to assist you in responding to the queries posed by the user:

{tools}
        """

        agent_tool_usage = """Use the following steps:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

GUIDELINES on the Use of Tools:
- Do not use any tool for answering simple questions (e.g., general knowledge, greetings, and conversational topics).
- Use the clinical_tool tool to download clinical trials only if the required information is not already available in the local CSV file.
- Use the python_repl_ast tool to retrieve information from the locally stored clinical trials dataset:
    - The dataset must be loaded into a Pandas DataFrame as follows: df = pandas.read_csv("db/ClinicalTrialsDB.csv").
    - Always verify the column names of the DataFrame at the start before executing any query to ensure the correct structure.
    - Always perform searches in lowercase to ensure case-insensitivity.
    - When extracting information from the dataset, do not limit yourself to exact matches with the query terms. Instead, interpret the available data to provide meaningful responses. For example, if a direct answer is not explicitly stated in the dataset, analyze relevant columns and infer the best possible answer based on the available information.
- Prioritize answers found in the set of downloaded clinical trials. If the necessary information is unavailable in the dataset, only then consider using PubMed.
- After providing the answer from the clinical trials dataset, if PubMed might be useful, ask the user if they want to use it.
- Use the pubmed_tool in the following cases:
    - To answer general medical questions that do not require clinical trial data.
    - When explicitly requested by the user to provide references from medical literature.
    - As a last resort, if no relevant information is found in the local dataset of clinical trials.
- When using a tool, refer to it directly by name, e.g., python_repl_ast."""

        agent_scratchpad = """Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        # Combine the agent's task, tool usage guidelines, and scratchpad into a single template
        template = "\n\n".join([agent_task, agent_tool_usage, agent_scratchpad])

        # Create a structured prompt using the template
        prompt = PromptTemplate.from_template(template)

        # Create a ReAct agent with the specified LLM, tools, and prompt
        agent = create_react_agent(
            llm,  # LLM instance to process the query
            tools,  # List of available tools
            prompt,  # The structured prompt guiding the agent's decision-making
        )

        # Create an agent executor by passing in the agent and tools
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # Enable verbose mode for debugging
            handle_parsing_errors=True,  # Handle parsing errors gracefully
        )

        # Invoke the agent with the query to get a response
        response = agent_executor.invoke({"input": question})

        # Print the output for debugging
        print("Query output: ", response["output"])  # Display the generated response

        # Return the output
        return response["output"]  # Extract and return the agent's response

    except Exception as e:
        # Handle any exceptions that occur during query execution
        print(f"An error occurred in react_agent: {e}")  # Log the error message
        return "It was not possible to generate an answer."  # Return a generic error message
