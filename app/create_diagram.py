import os
import graphviz  # For creating the workflow diagram
from IPython.display import display, Image

def create_detailed_workflow_diagram():
    """Creates a detailed workflow diagram."""
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="TB")  # Vertical layout

    # Main workflow nodes
    dot.node("START", "Start", shape="ellipse", style="filled", fillcolor="lightblue")
    dot.node("user_input", "User submits a question", shape="box", style="filled", fillcolor="lightgray")
    dot.node("generate_response", "generate_response()", shape="diamond", style="filled", fillcolor="lightyellow")
    dot.node("react_agent", "get_react_agent_response()", shape="parallelogram", style="filled", fillcolor="lightgreen")

    # ReAct agent decision-making nodes
    dot.node("decide_tool", "Agent decides the method", shape="diamond", style="filled", fillcolor="orange")
    dot.node("direct_answer", "Responds directly", shape="box", style="filled", fillcolor="lightgray")
    dot.node("clinical_tool", "Fetches clinical trials (ClinicalTrials.gov)", shape="parallelogram", style="filled", fillcolor="lightcoral")
    dot.node("csv_search", "Searches local dataset (CSV)", shape="parallelogram", style="filled", fillcolor="lightcoral")
    dot.node("pubmed", "Asks user for PubMed search", shape="parallelogram", style="filled", fillcolor="lightcoral")

    # Final response node
    dot.node("final_response", "Returns response to user", shape="box", style="filled", fillcolor="lightgray")
    dot.node("END", "End", shape="ellipse", style="filled", fillcolor="lightblue")

    # Connecting nodes
    dot.edge("START", "user_input", label="User asks a question")
    dot.edge("user_input", "generate_response", label="Passes messages")
    dot.edge("generate_response", "react_agent", label="Sends to get_react_agent_response()")
    dot.edge("react_agent", "decide_tool", label="Agent analyzes the question")

    # Agent decision paths
    dot.edge("decide_tool", "direct_answer", label="Simple question", style="dashed")
    dot.edge("decide_tool", "clinical_tool", label="Needs clinical data", style="dashed")
    dot.edge("decide_tool", "csv_search", label="Searches local CSV", style="dashed")
    dot.edge("csv_search", "final_response", label="Found in local data")
    dot.edge("decide_tool", "pubmed", label="Asks if PubMed should be used", style="dashed")

    # Returning responses
    dot.edge("direct_answer", "final_response")
    dot.edge("clinical_tool", "final_response")
    dot.edge("pubmed", "final_response")
    dot.edge("final_response", "END")

    # Save and display the diagram
    download_path = os.path.expanduser("~/Downloads/detailed_workflow_diagram")
    dot.render(download_path, format="png", cleanup=False)
    display(Image(filename=f"{download_path}.png"))

# Generate the diagram
create_detailed_workflow_diagram()
