from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

class AgentState(TypedDict, total=False):
    # Core conversation
    messages: List[Dict[str, str]]
    query: str
    intent: str
    portfolio_context: str
    
    # Contact Agent workflow state
    contact_step: Optional[str]  # 'idle', 'asking_name', 'asking_email', 'asking_subject', 'asking_message', 'asking_confirmation', 'submitted'
    name: Optional[str]
    email: Optional[str]
    subject: Optional[str]
    message: Optional[str]
    contact_confirmation: Optional[bool]
    contact_submission_status: Optional[str]  # 'not_started', 'pending_confirmation', 'success', 'failed'

    # Output response
    response: str
    response_type: str  # 'text', 'link', 'contact_prompt', 'contact_success', 'contact_error'
    url: Optional[str]
    quick_actions: Optional[List[str]]
