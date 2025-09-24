"""
Risk agent module for handling risk-related tasks.
"""

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage

from utils.time import get_today_str
from utils.logging import logger
from config import get_config
from prompts.agents import RISK_AGENT_SYSTEM_MESSAGE
from memory.state import ResearcherState, ResearcherOutputState
from agents.common import tools, tool_node, compress_research, should_continue


config = get_config()

risk_prompt = RISK_AGENT_SYSTEM_MESSAGE.format(date=get_today_str())

llm = config.llm.bind_tools(tools)

def risk_research_llm(state: ResearcherState) -> dict:
    """Analyze current state and decide on next actions.
    
    The model analyzes the current conversation state and decides whether to:
    1. Call search tools to gather more information
    2. Provide a final answer based on gathered information
    
    Returns updated state with the model's response.
    """
    logger.debug(f"@node risk_research_llm")
    
    return {
        "researcher_messages": [
            llm.invoke(
                [SystemMessage(content=risk_prompt)] + state["researcher_messages"]
            )
        ]
    }

agent_builder = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

RESEARCHER_NAME = "risk_researcher"
TOOL_NODE_NAME = "tool_node"
COMPRESS_RESEARCH_NAME = "compress_research"
# Nodes
agent_builder.add_node(RESEARCHER_NAME, risk_research_llm)
agent_builder.add_node(TOOL_NODE_NAME, tool_node)
agent_builder.add_node(COMPRESS_RESEARCH_NAME, compress_research)

# Edges
agent_builder.add_edge(START, RESEARCHER_NAME)
agent_builder.add_conditional_edges(
    RESEARCHER_NAME,
    should_continue,
    {
        TOOL_NODE_NAME: TOOL_NODE_NAME, # Continue research loop
        COMPRESS_RESEARCH_NAME: COMPRESS_RESEARCH_NAME, # Provide final answer
    },
)
agent_builder.add_edge(TOOL_NODE_NAME, RESEARCHER_NAME)
agent_builder.add_edge(COMPRESS_RESEARCH_NAME, END)

risk_agent = agent_builder.compile()

