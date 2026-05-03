import sqlite3
import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import AgentState
from .nodes import extract_and_match_node, human_review_node, draft_email_node

if not os.path.exists("data"):
    os.makedirs("data")

conn = sqlite3.connect("data/hr_workflow.db", check_same_thread=False)
memory = SqliteSaver(conn)

workflow = StateGraph(AgentState)

workflow.add_node("analyze", extract_and_match_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("draft_email", draft_email_node)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "human_review")
workflow.add_edge("human_review", "draft_email")
workflow.add_edge("draft_email", END)

app_agent = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)