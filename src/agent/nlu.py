from typing import Literal, Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from src.config.settings import OPENAI_API_KEY, OPENAI_MODEL


class UserCommand(BaseModel):
    """Structured output from user message parsing."""
    
    intent: Literal[
        "choose_service",
        "provide_field",
        "confirm_documents",
        "choose_option",
        "reset",
        "unknown"
    ] = Field(description="User's intent")
    
    service: Optional[Literal["birth_certificate", "id_appointment"]] = Field(
        default=None,
        description="Service type if user is choosing a service"
    )
    
    fields: dict = Field(
        default_factory=dict,
        description="Extracted field values. Keys can include: child_name, date_of_birth, sex, father_name, mother_name, age, has_previous_id, appointment_slot, print_option, etc. Only include fields that user explicitly provided."
    )
    
    choice: Optional[str] = Field(
        default=None,
        description="User's choice (A, B, C, D, DONE, etc.)"
    )
    
    language: Optional[Literal["am", "en"]] = Field(
        default=None,
        description="Detected language preference"
    )


def parse_user_message(message: str, state: str, language: str) -> UserCommand:
    """
    Parse user message using LLM to extract structured information.
    
    Args:
        message: User's input message
        state: Current state in the workflow
        language: Current language setting
        
    Returns:
        UserCommand with extracted information
    """
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0.2,
        api_key=OPENAI_API_KEY
    )
    
    structured_llm = llm.with_structured_output(UserCommand, method="function_calling")
    
    system_prompt = f"""You are a clerk assistant for Ethiopian kebele services. 
Your job is to extract information from user messages accurately.

Rules:
1. Extract ONLY what the user explicitly provided. Never invent or guess missing information.
2. If user answers with A/B/C/D, treat it as a choice and set intent to "choose_option".
3. Keep dates in DD/MM/YYYY format when possible.
4. For sex/gender, normalize to "Male" or "Female" (or "Boy"/"Girl").
5. If user provides multiple fields at once (e.g., "My child is Tadesse Taffa born 12/10/2020, boy"), extract all fields into the fields dict.
6. If intent is unclear, use "unknown".
7. For service selection, detect if user wants birth certificate or ID appointment and set intent to "choose_service".
8. Current state: {state}
9. Current language: {language}

Field names to use:
- child_name, date_of_birth (or dob), sex, father_name, mother_name
- age, has_previous_id, appointment_slot (A/B/C/D), print_option

Be precise and only extract what is clearly stated."""
    
    try:
        # Format prompt with system and user messages
        prompt = f"{system_prompt}\n\nUser message: {message}"
        result = structured_llm.invoke(prompt)
        return result
    except Exception as e:
        print(f"Error parsing user message: {e}")
        # Fallback: check for simple choices
        msg_upper = message.strip().upper()
        if msg_upper in ["A", "B", "C", "D", "DONE"]:
            return UserCommand(intent="choose_option", choice=msg_upper, fields={})
        # Return a safe default
        return UserCommand(intent="unknown", fields={})

