# app.rag_agent.clinical_tool.clinical_trials_search_tool.py
import os

from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import pandas as pd
from typing import Optional

from app import Config
# Importing required utility functions from the application module
from app.rag_agent.clinical_tool.web_search import get_web_search_chain
from app.rag_agent.clinical_tool.utils import (
    build_url_from_web_search,
    append_csv_from_url,
    append_json_from_url,
    process_json_studies_results,
    clear_json_file,
)

class ClinicalSearchTool(BaseTool):
    """
    A LangChain tool for searching clinical trials using ClinicalTrials.gov API.
    It refines the query using web search, retrieves data in CSV and JSON formats,
    processes the results, and provides a Pandas DataFrame as output.
    """

    name: str = "ClinicalTrialsSearch"  # Tool name
    description: str = """
    This tool is useful for answering questions with information based on clinical trials. 
    It queries the ClinicalTrials.gov endpoint to search for relevant clinical trials and related studies, given the following information:
    - A disease (e.g., lung cancer, breast cancer, and heart attack).
     - A specific intervention, such as:
        - A drug name
        - Medical devices, procedures, or vaccines
        - Non-invasive methods (e.g., educational programs, dietary changes, or exercise).
    - Aggregation filters to refine results based on study outcomes:
        - "with" (for studies that include results)
        - "without" (for studies without results)
    - The NCT Number: it indicates the NCT (National Clinical Trial) identifier of a study, if available.
    The retrieved data is then stored locally in CSV format.

    Input: A search query specifying the disease, NCT identifier, intervention, and/or result-based filtering.
    Output: The downloaded and processed clinical trials data, stored in the following CSV file: db/ClinicalTrialsDB.csv
    """

    def _run(self, question: str, callback_manager: Optional[CallbackManagerForToolRun] = None)->pd.DataFrame:
        """
        Executes the clinical trial search and returns a Pandas DataFrame containing results.
        """
        try:
            print("Searching ClinicalTrials.gov...")
            print("User query for clinical trials search:", question)

            # Perform a web search to refine the clinical trial query
            web_search_params = get_web_search_chain(
                model_name=self.selected_model,
                api_key=self.api_key,
            ).invoke(question)
            print("Web search parameters:", web_search_params)

            # Generate URLs for retrieving CSV and JSON data from ClinicalTrials.gov
            url_csv = build_url_from_web_search(web_search_params, "csv")
            url_json = build_url_from_web_search(web_search_params, "json")

            # Download and store clinical trial data in both CSV and JSON formats
            append_csv_from_url(url_csv)
            append_json_from_url(url_json)

            # Process the JSON results to extract relevant data
            process_json_studies_results()

            # Clean up the JSON file after processing
            clear_json_file()

            # Validate if the CSV file exists and is not empty before reading
            if os.path.exists(Config.CSV_PATH) and os.path.getsize(Config.CSV_PATH) > 0:
                df = pd.read_csv(Config.CSV_PATH)
            else:
                df = pd.DataFrame({"error": ["CSV file missing or empty"]})

            return df

        except Exception as e:
            # Handle exceptions gracefully and return an error message
            return pd.DataFrame({"error": [f"Error during clinical trial search: {e}"]})

    async def _arun(self, question: str) -> None:
        """
        This tool does not support asynchronous execution.
        """
        raise NotImplementedError("ClinicalSearchTool does not support asynchronous execution.")
    selected_model: str = ""
    api_key: str = ""
