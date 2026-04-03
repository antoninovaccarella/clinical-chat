import io
import os
import json
from urllib.parse import urlencode
import pandas as pd
import requests
from app import Config
from app.rag_agent.clinical_tool.web_search import WebSearch


# Method that, given a WebSearch object, constructs a URL for the ClinicalTrials.gov API specifications
def build_url_from_web_search(web_search: WebSearch, format_type: str) -> str:
    """
    Transforms a WebSearch object into a URL for the ClinicalTrials.gov API.

    Args:
        web_search (WebSearch): The object containing the search parameters.
        format_type (str): The format of the URL.


    Returns:
        str: The generated URL with the search parameters.
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    format_single_study = "?format="+format_type
    # Checks if an NCT ID is present
    if web_search.nctId:
        return f"{base_url}/{web_search.nctId}{format_single_study}"

    # Preparing the parameters as a dictionary
    params = {
        "format": format_type,  # Specifies the format of the response as JSON.
        "markupFormat": "markdown", #Specifies the format of the markup as Markdown.
        "query.cond": web_search.query_cond,  # Condition query parameter.
        "query.intr": web_search.query_intr,  # Intervention query parameter.
        "aggFilters": f"results:{web_search.aggFilters}" if web_search.aggFilters else None, # Aggregation filters.
        "pageSize": 500,  # Number of results per page.
    }

    # Removing parameters that have a None value
    filtered_params = {key: value for key, value in params.items() if value is not None}

    # Constructing the URL with urllib.parse.urlencode
    query_string = urlencode(filtered_params, safe=",")  # safe="|," preserves the special separators | and ,
    url = f"{base_url}?{query_string}"

    return url

def get_data(url):
    """
    Makes a GET request to the specified URL and returns the response content as JSON.

    Args:
        url (str): The URL from which to retrieve the data.

    Returns:
        dict: The data in JSON format, or a dictionary with an error message.
    """

    # Print the URL being requested. Useful for debugging.
    print(f"Making request to: {url}")

    try:
        # Attempt to make a GET request to the specified URL, with a 10-second timeout.
        response = requests.get(url, timeout=10)

        # Check if the response has a 200 (OK) status code.
        if response.status_code == 200:
            try:
                # Attempt to convert the response content to JSON format.
                return response.json()
            except ValueError:
                # If the JSON conversion fails, print an error message and return a dictionary with the error.
                print("Error: Unable to parse JSON response.")
                return {"error": "Failed to parse JSON response"}
        else:
            # If the response has a status code other than 200, print an error message with the status code and response text.
            print(f"HTTP Error {response.status_code}: {response.text}")
            return {"error": f"HTTP error {response.status_code}", "details": response.text}

    # Handle the timeout exception, if the request takes too long to complete.
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        return {"error": "Request timed out"}

    # Handle the connection error exception, if a connection problem occurs during the request.
    except requests.exceptions.ConnectionError:
        print("Error: Connection problem.")
        return {"error": "Connection error"}

    # Handle all other exceptions that may occur during the request.
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def append_csv_from_url(url):
    file_path = Config.CSV_PATH

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Leggi il CSV scaricato
        try:
            df_new = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        except pd.errors.ParserError as e:
            print(f"Error parsing downloaded CSV: {e}")
            return

        if df_new.empty:
            print("Downloaded CSV is empty.")
            return

        nct_index_name = "NCT Number" #Nome della colonna che contiene l'NCT number
        try:
            nct_index = df_new.columns.get_loc(nct_index_name) #Ottieni l'indice della colonna NCT number
        except KeyError:
            print(f"Downloaded CSV lacks '{nct_index_name}' column.")
            return

        file_exists = os.path.exists(file_path)

        if file_exists:
            try:
                df_existing = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:  # Gestisci il caso di file esistente ma vuoto
                df_existing = pd.DataFrame(columns=df_new.columns)  # Crea un DataFrame vuoto con le stesse colonne

            if df_existing.empty: #se il file esiste ma è vuoto
                df_new.to_csv(file_path, mode='w', index=False, encoding = 'utf-8')
            else:
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined.drop_duplicates(subset=nct_index_name, keep='first', inplace=True)
                df_combined.to_csv(file_path, mode='w', index=False, encoding='utf-8')  # Sovrascrivi con i dati combinati

        else:  # Prima iterazione (file non esistente)
            df_new.to_csv(file_path, mode='w', index=False, encoding='utf-8') #Scrivi tutto il df

        print(f"Data appended/written to {file_path}.")

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"A general error occurred: {e}")


def append_json_from_url(url):
    """
    Retrieves data from a URL, and writes it to a JSON file. Overwrites the file if it exists.

    Args:
        url (str): The URL to retrieve data from.
    """

    # Path to the JSON file, retrieved from a configuration class (presumably).
    path_file = Config.JSON_PATH  # Assumes Config.JSON_PATH is defined elsewhere

    # Retrieve data from the URL using the get_data function (defined elsewhere).
    clinical_data = get_data(url)  # Assumes get_data handles potential errors and returns a dict.

    # Open the file in write mode ('w'). This will *overwrite* the file if it exists.
    with open(path_file, 'w') as file:
        # Write the retrieved data to the JSON file, with indentation for readability.
        json.dump(clinical_data, file, indent=4) # Uses json.dump to write the dictionary to a file

def clear_csv_file() -> None:
    """
    Clears the contents of the specified CSV file.
    """
    file_path = Config.CSV_PATH
    try:
        # Open the file in write mode ('w') to truncate it.
        with open(file_path, 'w') as file:
            pass  # Do nothing, effectively clearing the file.
        print(f"File '{file_path}' cleared successfully.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except PermissionError:
        print(f"Error: Insufficient permissions to modify file '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while clearing the file: {e}")

def clear_json_file():
    """
    Clears the contents of the JSON file by writing an empty list to it.
    """
    # Path to the JSON file, retrieved from a configuration class (presumably).
    path_file = Config.JSON_PATH

    try:
        # Open the file in write mode ('w'). This will overwrite the existing content.
        with open(path_file, 'w') as file:
            # Write an empty list to the file, effectively clearing its contents.
            json.dump([], file, indent=4)  # Writes an empty JSON list
        print(f"JSON file '{path_file}' cleared.")
    except Exception as e:  # Catch any potential errors during file operations
        print(f"An error occurred while clearing the JSON file: {e}")


def reset_clinical_trials_storage() -> None:
    """
    Resets the local ClinicalTrials cache files used by the application.
    """
    clear_csv_file()
    clear_json_file()

## Functions for Participant Flow column and Outcomes update from json.
def process_json_studies_results():
    """
    Processes JSON study results and updates the corresponding CSV file with extracted outcome measures.
    """
    json_file_path = Config.JSON_PATH
    csv_file_path = Config.CSV_PATH

    # Load CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: Empty CSV file at {csv_file_path}")
        return
    except pd.errors.ParserError:
        print(f"Error: CSV file could not be parsed at {csv_file_path}")
        return

    # Load JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return

    # Ensure the "studies" key exists in the JSON data
    if not "studies" in data:
        data["studies"] = [data]

    studies = data.get('studies', [])
    nct_numbers_df = set(df['NCT Number'].astype(str))  # Convert to set for faster lookup

    # Convert relevant columns to object type
    df['Primary Outcome Measures'] = df['Primary Outcome Measures'].astype(object)
    df['Secondary Outcome Measures'] = df['Secondary Outcome Measures'].astype(object)
    df['Other Outcome Measures'] = df['Other Outcome Measures'].astype(object)

    # Create a new column 'Participant Flow' and initialize with None
    if "Participant Flow" not in df.columns:
        df['Participant Flow'] = None
    # Process each study
    for study in studies:
        nct_id = study.get('protocolSection', {}).get('identificationModule', {}).get('nctId')
        if nct_id and nct_id in nct_numbers_df:  # Check if nct_id is valid and exists in the DataFrame
            # Extract recruitment details
            recruitment_details = study.get('resultsSection', {}).get('participantFlowModule', {}).get('recruitmentDetails')
            # Get the existing outcome values
            existing_primary = df.loc[df['NCT Number'] == nct_id, 'Primary Outcome Measures'].iloc[0]
            existing_secondary = df.loc[df['NCT Number'] == nct_id, 'Secondary Outcome Measures'].iloc[0]
            existing_other = df.loc[df['NCT Number'] == nct_id, 'Other Outcome Measures'].iloc[0]

            # Update the 'Participant Flow' column for the corresponding NCT Number
            df.loc[df['NCT Number'] == nct_id, 'Participant Flow'] = recruitment_details

            # Extract and update outcome measures
            results_primary = extract_outcome_info(study, "primary")
            # print("results_primary = ", results_primary)
            updated_primary = update_outcome(existing_primary, results_primary)
            df.loc[df['NCT Number'] == nct_id, 'Primary Outcome Measures'] = updated_primary

            results_secondary = extract_outcome_info(study, "secondary")
            # print("results_secondary = ", results_secondary)
            updated_secondary = update_outcome(existing_secondary, results_secondary)
            df.loc[df['NCT Number'] == nct_id, 'Secondary Outcome Measures'] = updated_secondary

            results_other = extract_outcome_info(study, "other")
            # print("results_other = ", results_other)
            updated_other = update_outcome(existing_other, results_other)
            df.loc[df['NCT Number'] == nct_id, 'Other Outcome Measures'] = updated_other

    # Save the updated DataFrame to the CSV file
    try:
        df.to_csv(csv_file_path, index=False)
        print(f"DataFrame updated and saved to {csv_file_path}")
    except Exception as e:
        print(f"Error saving DataFrame to CSV: {e}")

def extract_outcome_info(study, outcome_type):
    """
    Extracts outcome information from a study based on the specified outcome type.

    Args:
        study (dict): The study data containing outcome measures.
        outcome_type (str): The type of outcome to extract ("primary", "secondary", or "other").

    Returns:
        list: A list of dictionaries containing the extracted outcome details.
    """
    outcome_measures = study.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
    results = []

    for outcome in outcome_measures:
        if outcome_type.lower() == "other":
            if outcome.get("type", "").lower() not in ("primary", "secondary"):
                results.append(extract_outcome_details(outcome))
        elif outcome.get("type", "").lower() == outcome_type.lower():
            results.append(extract_outcome_details(outcome))

    return results

def extract_outcome_details(outcome):
    """
    Extracts detailed information from an outcome measure.

    Args:
        outcome (dict): The outcome measure data.

    Returns:
        dict: A dictionary containing the extracted outcome details.
    """
    info = {
        "title": outcome.get("title"),
        "description": outcome.get("description"),
        "populationDescription": outcome.get("populationDescription", "N/A"),
        # "type": outcome.get("type", "N/A"),
        "timeFrame": outcome.get("timeFrame", "N/A")
    }
    analyses = outcome.get("analyses", [])  # Get the list of analyses, default to empty list

    # Check if there are any analyses
    if analyses:
        analysis = analyses[0]  # Take the first analysis
        info.update({key: analysis.get(key) for key in ("paramType", "paramValue", "pValue", "statisticalMethod", "ciPctValue", "ciNumSides", "ciLowerLimit","ciUpperLimit","estimateComment") if key in analysis})

    return info

def update_outcome(existing_outcome, new_results):
    """
    Updates the outcome information in the DataFrame by appending new results
    to the existing outcome string, handling multiple outcomes separated by '|'.
    Structures the output in the new format.

    Args:
        existing_outcome (str): The current outcome value in the DataFrame.
        new_results (list): A list of new outcome results.

    Returns:
        str: The updated outcome string with new results appended in the new format.
    """


    # Split the existing outcome into individual outcomes using "|"
    existing_outcomes = existing_outcome.split("|") if isinstance(existing_outcome, str) else []

    # Append new results to each existing outcome
    updated_outcomes = []
    for i, outcome in enumerate(existing_outcomes):
        outcome = outcome.strip()  # Remove leading/trailing whitespace
        if outcome:  # Check if the outcome is not empty
            # Split the outcome into title and description
            if outcome.startswith("TITLE:"):
                updated_outcomes.append(outcome)
                continue
            if not new_results:
                fields = outcome.split(',')
                if len(fields) == 3:
                    new_result_str = (
                        f"TITLE: {fields[0]}\n" 
                        f"DESCRIPTION: {fields[1]}\n\n"
                        f"TIMEFRAME: {fields[2]}\n\n"
                    )
                else:
                    new_result_str = (" ".join(fields))
                updated_outcomes.append(new_result_str)
                continue  # Skip to the next outcome
        # Append new results to the existing outcome
            if new_results:
                if i < len(new_results):
                    pvalue = new_results[i].get('pValue', 'N/A')
                    statisticalMethod = new_results[i].get('statisticalMethod', 'N/A')
                    paramType = new_results[i].get('paramType', 'N/A')
                    paramValue = new_results[i].get('paramValue', 'N/A')
                    ciPctValue = new_results[i].get('ciPctValue', 'N/A')
                    ciNumSides = new_results[i].get('ciNumSides', 'N/A')
                    ciLowerLimit = new_results[i].get('ciLowerLimit', 'N/A')
                    ciUpperLimit = new_results[i].get('ciUpperLimit', 'N/A')
                    estimateComment = new_results[i].get('estimateComment', 'N/A')

                    new_result_str = (
                        f"TITLE: {new_results[i]['title']}\n"
                        f"DESCRIPTION: {new_results[i]['description']}\n"
                        f"POPULATION DESCRIPTION: {new_results[i].get('populationDescription', 'N/A')}\n"
                        f"TIME_FRAME: {new_results[i].get('timeFrame', 'N/A')}\n"
                    )
                    # Add pValue and statisticalMethod only if not N/A
                    if pvalue!= "N/A" or statisticalMethod!= "N/A":
                         new_result_str += "STATISTICAL_TEST: \n"
                         new_result_str += (
                            f"P_VALUE = {pvalue}\n"
                            f"STATISTICAL_METHOD = {statisticalMethod}\n\n"
                        )

                    # Add ciPctValue, ciNumSides, ciLowerLimit, ciUpperLimit, estimateComment only if not N/A
                    if any(value!= "N/A" for value in [paramType, paramValue, ciPctValue, ciNumSides, ciLowerLimit, ciUpperLimit, estimateComment]):
                        new_result_str += "STATISTICAL_TEST: \n"
                        new_result_str += (
                            f"ESTIMATION_PARAMETER = {paramType}\n"
                            f"ESTIMATED_VALUE = {paramValue}\n"
                            f"CONFIDENCE_INTERVAL_VALUE = {ciPctValue}%\n"
                            f"SIDES = {ciNumSides}\n"
                            f"CONFIDENCE_INTERVAL_LOWER_LIMIT = {ciLowerLimit}\n"
                            f"CONFIDENCE_INTERVAL_UPPER_LIMIT = {ciUpperLimit}\n"
                            f"ESTIMATION_COMMENTS = {estimateComment}\n\n"
                        )
                    updated_outcome = f"{new_result_str}"  # Use only the new format
            else:
                updated_outcome = outcome  # Keep the original outcome if no corresponding new result
            updated_outcomes.append(updated_outcome)

    # Join the updated outcomes with "|" and then replace "|" with "\n"
    return "\n".join(updated_outcomes)  # Use newline as separator
