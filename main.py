from pydantic_ai import Agent, Tool
from pydantic import BaseModel,Field

#Defining what a single red flag would look like
class RedFlag(BaseModel):
    item: str = Field(description="The specific text, clause, or sentence from the document that is a red flag.")
    severity: str = Field(description="The severity level of the red flag, such as 'High', 'Medium', or 'Low'.")
    reason: str = Field(description="A brief explanation of why this item is considered a red flag.")

#Defining the container to hold all the red flags found in the document
class RedFlagReport(BaseModel):
    document_summary: str = Field(description="A brief summary of the document being analyzed.")
    red_flags: list[RedFlag] = Field(description="A list of all the red flags identified in the document.")

#Defining agent
import os
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv


groq_api_key = os.environ.get("GROQ_API_KEY") #for universersal api key access
if not groq_api_key:
    load_dotenv() #for local api key access
    
model_instance=GroqModel(
    model_name="groq:llama-3.3-70b-versatile",
    )
agent = Agent(
    model=model_instance,
    instructions=(
        "You are an expert legal and document risk analyst. "
        "Your task is to review the provided text and identify any 'red flags'—such as "
        "unfair clauses, hidden fees, high-risk commitments, or ambiguous rules. "
        "Be thorough and objectively judge the severity of each risk."
    ),
    output_type=RedFlagReport

)

def red_flag_analyzer(query_text):
    return agent.run_sync(query_text).output


if __name__ == "__main__":
    sample_document = """
TERMS OF SERVICE Agreement:
Users must pay a non-refundable entry fee of $500. The company reserves the right to 
change the fee amount at any time without prior notice to the user. Furthermore, 
the company can terminate any user account for any reason or no reason at all, 
and all user data will be deleted immediately upon termination. Any disputes 
arising from this agreement must be resolved exclusively via binding arbitration 
held in the Cayman Islands, and the user waives all rights to a jury trial or class action.
"""

    print("Analyzing document for red flags...")

    result = agent.run_sync(sample_document)

    print("\n--- ANALYSIS COMPLETED ---")
    print(f"Document Summary: {result.output.document_summary}\n")
    print(f"Red flag found:{len(result.output.red_flags)}")
    print("Here is the list of red flags")
    for i,flag in enumerate(result.output.red_flags):
        print(f"Red flag {i}:\nitem: {flag.item}\nSeverity: {flag.severity}\nReason: {flag.reason}")

    print("Thats all")
