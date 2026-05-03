import json
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.groq import Groq
from .state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
llm = Groq(model="llama-3.3-70b-versatile", api_key=api_key)

def extract_and_match_node(state: AgentState):
    documents = SimpleDirectoryReader(input_files=[state['cv_path']]).load_data()
    cv_text = "\n".join([doc.text for doc in documents])
    
    prompt = (
        f"Analyze this CV and compare with JD: {state['jd_text']}\n"
        "Extract Name, Email and match CV with JD.\n"
        "RETURN JSON ONLY:\n"
        '{"full_name": "Name", "email": "Email", "score": 85, "reasoning": "..."}'
    )
    
    response = llm.complete(f"{prompt}\n\nCV Content: {cv_text}")
    try:
        content = response.text
        result = json.loads(content[content.find('{'):content.rfind('}')+1])
    except:
        result = {"score": 0, "reasoning": "Error"}
    
    return {
        "candidate_name": result.get('full_name', "Candidate"),
        "candidate_info": result,
        "matching_score": result.get('score', 0),
        "reasoning": result.get('reasoning', ""),
        "hr_decision": "pending"
    }

def draft_email_node(state: AgentState):
    decision = state.get("hr_decision")
    candidate_name = state.get("candidate_name", "Candidate")
    
    if decision == "approved":
        purpose = "an interview invitation"
        tone_instruction = "congratulatory, professional, and inviting"
        specific_instruction = "Ask for their availability for a 30-minute interview call."
    else:
        purpose = "a polite rejection email (thank you letter)"
        tone_instruction = "respectful, professional, and encouraging"
        specific_instruction = "Thank them for their time and mention that we will keep their CV in our talent pool for future opportunities."

    prompt = (
        f"You are an HR Specialist at WSP. Write a professional {purpose} to {candidate_name}.\n"
        f"Context: The HR manager has reviewed the CV and {decision} the application.\n"
        "Requirements:\n"
        "- Use HTML tags: <br> for line breaks, <p> for paragraphs.\n"
        f"- {specific_instruction}\n"
        "- Keep it concise and professional.\n"
        "- Sign strictly as 'WSP Recruitment Team'.\n"
        "Return JSON ONLY in this structure: "
        '{"subject": "Interview Invitation - WSP", "content": "HTML_CONTENT_HERE"}'
    )
    
    response = llm.complete(prompt)
    
    try:
        content = response.text
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        result = json.loads(content[start_idx:end_idx])
    except:
        result = {
            "subject": "Update regarding your application",
            "content": f"Your application status has been updated to: {decision}."
        }
    
    return {
        "messages": [f"Email drafted for decision: {decision}"],
        "email_draft": result 
    }


def human_review_node(state: AgentState):
    pass