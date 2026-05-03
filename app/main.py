import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from .graph import app_agent

app = FastAPI()

@app.post("/start-screening")
async def start_screening(file: UploadFile = File(...), jd_text: str = Form(...)):
    temp_path = f"data/temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    app_agent.invoke({"cv_path": temp_path, "jd_text": jd_text}, config)
    
    final_state = app_agent.get_state(config).values
    if os.path.exists(temp_path): os.remove(temp_path)
    
    return {
        "thread_id": thread_id,
        "score": final_state.get('matching_score'),
        "reasoning": final_state.get('reasoning')
    }

@app.post("/hr-approve")
async def hr_approve(thread_id: str, decision: str):
    config = {"configurable": {"thread_id": thread_id}}
    app_agent.update_state(config, {"hr_decision": decision}, as_node="human_review")
    app_agent.invoke(None, config)
    
    final_state = app_agent.get_state(config).values
    
    candidate_info = final_state.get("candidate_info", {})
    candidate_email = candidate_info.get("email", "")

    draft = final_state.get("email_draft", {})

    return {
        "status": "success",
        "candidate_email": candidate_email, 
        "email_subject": draft.get("subject", "Update from WSP"),
        "email_content": draft.get("content", "")
    }