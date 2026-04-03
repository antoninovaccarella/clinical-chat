# app.rag_agent.clinical_tool.web_search.py

# Import necessary modules
from typing import Optional  # For optional type hinting
from langchain_core.output_parsers import PydanticOutputParser  # For parsing LLM output into Pydantic objects
from langchain_core.prompts import PromptTemplate  # For creating prompt templates
from pydantic import BaseModel, Field  # For defining data models using Pydantic
from app.large_language_models import get_chat_model

# Define the Pydantic model for web search parameters
class WebSearch(BaseModel):
    """
    Pydantic model for structuring the output of the web search query generation.
    This defines the expected format of the information extracted from the user's question,
    which is then used to construct the actual web search query.

    Attributes:
        query_cond: The condition or disease being queried. Optional.
        nctId: The National Clinical Trial (NCT) identifier. Optional.
    """

    query_cond: Optional[str] = Field(
        description=(
            """
            The disease.
            Examples:
            - lung cancer
            - breast cancer
            - heart attack
            """
        )  # Provides clear examples of what should be in this field.
    )

    nctId: Optional[str] = Field(
        description=(
            """
            This field must contain the NCT (National Clinical Trial) identifier of a study, if available.  This allows for direct retrieval of specific studies.
            """
        )  # Explains the purpose of the NCT identifier and its importance for direct retrieval.
    )

    query_intr: Optional[str] = Field(
        description=(
            """
            The specific intervention.
            Examples:
            - a specific drug name
            - medical devices, procedures, vaccines
            - non-invasive methods such as educational programs, changes to diet, and exercise.
            The field must not be included if the information is not present.  This allows for queries where the intervention is not specified.
            """
        )
    )

    aggFilters: Optional[str] = Field(
        description=(
            """
            Filters studies based on whether they have results or not.
            Allowed values:
            - "with" (for studies with results)
            - "without" (for studies without results)
            Do not include any other values.  This ensures only valid filter values are used.
            The field must not be included if the information is not present.  This allows for queries without result filtering.
            """
        )
    )

    def get_cond(self):  # A getter method for the query_cond attribute.  While not strictly necessary in Python, it can be useful for consistency or future extensions.
        return self.query_cond

    def get_nct_number(self):  # A getter method for the nctId attribute.
        return self.nctId

# Create a Pydantic output parser
parser = PydanticOutputParser(pydantic_object=WebSearch)  # Configures the parser to expect output in the format defined by the WebSearch model. This is key for structured output parsing.

# Create the prompt template
prompt = PromptTemplate(
    template="You are an expert in analyzing and extracting only relevant fields from a user question.\n{format_instructions}\n{question}\n",
    input_variables=["question"],  # Specifies the input variable for the user's question.
    partial_variables={"format_instructions": parser.get_format_instructions()},  # Includes the format instructions from the parser in the prompt. These instructions are crucial as they tell the LLM *exactly* how to format its response so the parser can understand it.
)

def get_web_search_chain(model_name: str = "", api_key: str = ""):
    """
    Build the extraction chain lazily so the app can start even when no LLM API key is configured.
    """

    llm = get_chat_model(model_name=model_name, api_key=api_key)
    return prompt | llm | parser
