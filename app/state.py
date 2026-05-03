from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    cv_path: str
    jd_text: str
    candidate_name: str
    candidate_info: dict
    email_draft: dict
    matching_score: int
    reasoning: str
    hr_decision: str
    messages: Annotated[List[str], operator.add]