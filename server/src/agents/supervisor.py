"""Multi-agent supervisor for coordinating research across multiple specialized agents.

This module implements a supervisor pattern where:
1. A supervisor agent coordinates research activities and delegates tasks
2. Multiple researcher agents work on specific sub-topics independently
3. Results are aggregated and compressed for final reporting

The supervisor uses parallel research execution to improve efficiency while
maintaining isolated context windows for each research topic.
"""
import asyncio
from typing_extensions import Literal

from langchain_core.messages import (
    BaseMessage, 
    SystemMessage, 
    ToolMessage,
    filter_messages,
    HumanMessage
)
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from prompts.agents import SUPERVISOR_SYSTEM_MESSAGE
from memory.state import  SupervisorState
from utils.time import get_today_str
from config import get_config
from tools.think import think_tool
from tools.research import ResearchComplete, create_handoff_tool
from utils.logging import logger

from agents.legal import legal_agent
from agents.finance import finance_agent
from agents.governance import governance_agent
from agents.risk import risk_agent
from agents.reputation import reputation_agent

config = get_config()

# Handoffs
assign_to_finance_agent = create_handoff_tool(
    agent_name="finance_agent",
    description="Assign task to a finance agent.",
)

assign_to_legal_agent = create_handoff_tool(
    agent_name="legal_agent",
    description="Assign task to a legal agent.",
)

assign_to_governance_agent = create_handoff_tool(
    agent_name="governance_agent",
    description="Assign task to a governance agent.",
)

assign_to_risk_agent = create_handoff_tool(
    agent_name="risk_agent",
    description="Assign task to a risk agent.",
)

assign_to_reputation_agent = create_handoff_tool(
    agent_name="reputation_agent",
    description="Assign task to a reputation agent.",
)


def get_notes_from_tool_calls(messages: list[BaseMessage]) -> list[str]:
    """Extract research notes from ToolMessage objects in supervisor message history.

    This function retrieves the compressed research findings that sub-agents
    return as ToolMessage content. When the supervisor delegates research to
    sub-agents via ConductResearch tool calls, each sub-agent returns its
    compressed findings as the content of a ToolMessage. This function
    extracts all such ToolMessage content to compile the final research notes.

    Args:
        messages: List of messages from supervisor's conversation history

    Returns:
        List of research note strings extracted from ToolMessage objects
    """
    return [tool_msg.content for tool_msg in filter_messages(messages, include_types="tool")]


supervisor_tools = [ResearchComplete, think_tool, assign_to_finance_agent, assign_to_legal_agent, assign_to_governance_agent, assign_to_risk_agent, assign_to_reputation_agent]
supervisor_model = config.llm
supervisor_model_with_tools = supervisor_model.bind_tools(supervisor_tools)

# System constants
# Maximum number of tool call iterations for individual researcher agents
# This prevents infinite loops and controls research depth per topic
MAX_RESEARCHER_ITERATIONS = 3 # Calls to think_tool + web_search + handoff to sub-agent

# Maximum number of concurrent research agents the supervisor can launch
# This is passed to the lead_researcher_prompt to limit parallel research tasks
MAX_CONCURRENT_RESEARCHERS = 3

# ===== SUPERVISOR NODES =====

async def supervisor(state: SupervisorState) -> Command[Literal["supervisor_tools"]]:
    """Coordinate research activities.

    Analyzes the research brief and current progress to decide:
    - What research topics need investigation
    - Whether to conduct parallel research
    - When research is complete

    Args:
        state: Current supervisor state with messages and research progress

    Returns:
        Command to proceed to supervisor_tools node with updated state
    """
    supervisor_messages = state.get("supervisor_messages", [])

    # Prepare system message with current date and constraints
    system_message = SUPERVISOR_SYSTEM_MESSAGE.format(
        date=get_today_str(), 
        max_concurrent_research_units=MAX_CONCURRENT_RESEARCHERS,
        max_researcher_iterations=MAX_RESEARCHER_ITERATIONS
    )
    messages = [SystemMessage(content=system_message)] + supervisor_messages

    # Make decision about next research steps
    response = await supervisor_model_with_tools.ainvoke(messages)

    return Command(
        goto="supervisor_tools",
        update={
            "supervisor_messages": [response],
            "research_iterations": state.get("research_iterations", 0) + 1
        }
    )

async def supervisor_tools(state: SupervisorState) -> Command[Literal["supervisor", "__end__"]]:
    """Execute supervisor decisions - either conduct research or end the process.

    Handles:
    - Executing think_tool calls for strategic reflection
    - Executing transfer_to_<agent> calls to delegate tasks to specialized agents
    - Launching parallel research agents for different topics
    - Research agents available are finance, governance, legal, reputation and risk
    - Aggregating research results
    - Determining when research is complete

    Args:
        state: Current supervisor state with messages and iteration count

    Returns:
        Command to continue supervision, end process, or handle errors
    """
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    most_recent_message = supervisor_messages[-1]

    logger.debug(f"@func supervisor_tools:  \n Research Iterations: {research_iterations} \n Most Recent Message Tool Calls: {most_recent_message.tool_calls} Supervisor messages: {supervisor_messages}")

    # Initialize variables for single return pattern
    tool_messages = []
    all_raw_notes = []
    next_step = "supervisor"  # Default next step
    should_end = False

    # Check exit criteria first
    exceeded_iterations = research_iterations >= MAX_RESEARCHER_ITERATIONS
    no_tool_calls = not most_recent_message.tool_calls
    research_complete = any(
        tool_call["name"] == "ResearchComplete" 
        for tool_call in most_recent_message.tool_calls
    )

    if exceeded_iterations or no_tool_calls or research_complete:
        should_end = True
        next_step = END

    else:
        # Execute ALL tool calls before deciding next step
        try:
            # Separate think_tool calls from ConductResearch calls
            think_tool_calls = [
                tool_call for tool_call in most_recent_message.tool_calls 
                if tool_call["name"] == "think_tool"
            ]

            conduct_research_calls = [
                tool_call for tool_call in most_recent_message.tool_calls 
                if tool_call["name"] in ["transfer_to_finance_agent", "transfer_to_legal_agent", "transfer_to_governance_agent", "transfer_to_risk_agent", "transfer_to_reputation_agent"]
            ]


            # Handle think_tool calls (synchronous)
            for tool_call in think_tool_calls:
                observation = think_tool.invoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(
                        content=observation,
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    )
                )


            # Handle ConductResearch calls (asynchronous)
            if conduct_research_calls:
                # Launch parallel research agents
                logger.debug(f"Launching {len(conduct_research_calls)} research agents {conduct_research_calls}")

                coros = []

                for tool_call in conduct_research_calls:
                    research_topic = tool_call["args"]["research_topic"]
                  
                    if tool_call["name"] == "transfer_to_legal_agent":

                        logger.debug(f"Assigning to legal agent for research topic: {research_topic}")
                        coros.append(
                            legal_agent.ainvoke({
                                "research_topic": research_topic,
                                "researcher_messages":[HumanMessage(content=research_topic)]
                            })
                        )
                    elif tool_call["name"] == "transfer_to_finance_agent":
                        logger.debug(f"Assigning to finance agent for research topic: {research_topic}")
                        coros.append(
                            finance_agent.ainvoke({
                                "research_topic": research_topic,
                                "researcher_messages":[HumanMessage(content=research_topic)]
                            })
                        )
                    elif tool_call["name"] == "transfer_to_governance_agent":
                        logger.debug(f"Assigning to governance agent for research topic: {research_topic}")
                        coros.append(
                            governance_agent.ainvoke({
                                "research_topic": research_topic,
                                "researcher_messages":[HumanMessage(content=research_topic)]
                            })
                        )
                    elif tool_call["name"] == "transfer_to_risk_agent":
                        logger.debug(f"Assigning to risk agent for research topic: {research_topic}")
                        coros.append(
                            risk_agent.ainvoke({
                                "research_topic": research_topic,
                                "researcher_messages":[HumanMessage(content=research_topic)]
                            })
                        )
                    elif tool_call["name"] == "transfer_to_reputation_agent":
                        logger.debug(f"Assigning to reputation agent for research topic: {research_topic}")
                        coros.append(
                            reputation_agent.ainvoke({
                                "research_topic": research_topic,
                                "researcher_messages":[HumanMessage(content=research_topic)]
                            })
                        )
                    else:
                        logger.warning(f"Unknown research agent: {tool_call['name']} for topic {research_topic}")
                        continue

                # Wait for all research to complete
                tool_results = await asyncio.gather(*coros)

                logger.debug(f"Research results: {tool_results}")

                # Format research results as tool messages
                # Each sub-agent returns compressed research findings in result["compressed_research"]
                # We write this compressed research as the content of a ToolMessage, which allows
                # the supervisor to later retrieve these findings via get_notes_from_tool_calls()
                research_tool_messages = [
                    ToolMessage(
                        content=result.get("compressed_research", "Error synthesizing research report"),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    ) for result, tool_call in zip(tool_results, conduct_research_calls)
                ]

                tool_messages.extend(research_tool_messages)

                # Aggregate raw notes from all research
                all_raw_notes = [
                    "\n".join(result.get("raw_notes", [])) 
                    for result in tool_results
                ]

        except Exception as e:
            logger.error(f"Error in supervisor tools: {e}")
            should_end = True
            next_step = END

    # Single return point with appropriate state updates
    if should_end:
        return Command(
            goto=next_step,
            update={
                "notes": get_notes_from_tool_calls(supervisor_messages),
                "research_brief": state.get("research_brief", "")
            }
        )
    else:
        return Command(
            goto=next_step,
            update={
                "supervisor_messages": tool_messages,
                "raw_notes": all_raw_notes
            }
        )
    


# ===== GRAPH CONSTRUCTION =====
RESEARCHER_NAME = "supervisor"
TOOL_NODE_NAME = "supervisor_tools"
# Build supervisor graph
supervisor_builder = (StateGraph(SupervisorState)
.add_node(RESEARCHER_NAME, supervisor)
.add_node(TOOL_NODE_NAME, supervisor_tools)
)


supervisor_builder.add_edge(START, RESEARCHER_NAME)
supervisor_agent = supervisor_builder.compile()