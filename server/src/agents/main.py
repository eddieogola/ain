"""
Full Multi-Agent Research System

This module integrates all components of the research system:
- User clarification and scoping
- Research brief generation  
- Multi-agent research coordination
- Final report generation

The system orchestrates the complete research workflow from initial user
input through final report delivery.
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from utils.time import get_today_str
from prompts.agents import FINAL_REPORT_GENERATION_SYSTEM_MESSAGE
from memory.state import AgentState, AgentInputState

from agents.common import clarify_with_user, write_research_brief
from agents.supervisor import supervisor_agent

from config import get_config
config = get_config()

async def final_report_generation(state: AgentState):
    """
    Final report generation node.
    
    Synthesizes all research findings into a comprehensive final report
    """
    
    notes = state.get("notes", [])
    
    findings = "\n".join(notes)

    final_report_prompt = FINAL_REPORT_GENERATION_SYSTEM_MESSAGE.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str()
    )
    
    final_report = await config.writer_llm.ainvoke([HumanMessage(content=final_report_prompt)])
    
    return {
        "final_report": final_report.content, 
        "messages": ["Here is the final report: " + final_report.content],
    }

# ===== GRAPH CONSTRUCTION =====
# Build the overall workflow
research_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
research_builder.add_node("clarify_with_user", clarify_with_user)
research_builder.add_node("write_research_brief", write_research_brief)
research_builder.add_node("supervisor_subgraph", supervisor_agent)
research_builder.add_node("final_report_generation", final_report_generation)

# Add workflow edges
research_builder.add_edge(START, "clarify_with_user")
research_builder.add_edge("write_research_brief", "supervisor_subgraph")
research_builder.add_edge("supervisor_subgraph", "final_report_generation")
research_builder.add_edge("final_report_generation", END)

# Compile the full workflow
agent = research_builder.compile()