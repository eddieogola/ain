from typing import Literal

from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage, filter_messages, AIMessage, get_buffer_string
from langgraph.types import Command
from langgraph.graph import  END

from utils.time import get_today_str
from utils.logging import logger
from config import get_config
from tools.search import web_search
from tools.think import think_tool
from prompts.agents import COMPRESS_RESEARCH_SYSTEM_MESSAGE, COMPRESS_RESEARCH_HUMAN_PROMPT, CLARIFY_WITH_USER_MESSAGE, TRANSFORM_MESSAGES_INTO_RESEARCH_TOPIC_MESSAGE

from memory.state import ResearcherState, AgentState, ClarifyWithUser, ResearchQuestion

config = get_config()

tools = [
    web_search,
    think_tool
]

tools_by_name = {tool.name: tool for tool in tools}

model = config.llm

def tool_node(state: ResearcherState) -> dict:
    """Execute all tool calls from the previous LLM response.
    
    Executes all tool calls from the previous LLM responses.
    Returns updated state with tool execution results.
    """
    tool_calls = state["researcher_messages"][-1].tool_calls
    
    # Execute all tool calls
    observations = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observations.append(tool.invoke(tool_call["args"]))
            
    # Create tool message outputs
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        ) for observation, tool_call in zip(observations, tool_calls)
    ]
    return {"researcher_messages": tool_outputs}

def compress_research(state: ResearcherState) -> dict:
    """Compress research findings into a concise summary.
    
    Takes all the research messages and tool outputs and creates
    a compressed summary suitable for the supervisor's decision-making.
    """
    logger.debug(f"@func compress_research: Researcher messages:Researcher Topic:{state.get('research_topic', '')} \n Researcher Messages: {state['researcher_messages']}")

    system_message = COMPRESS_RESEARCH_SYSTEM_MESSAGE.format(date=get_today_str())
    human_message = COMPRESS_RESEARCH_HUMAN_PROMPT.format(research_topic=state.get("research_topic", ""))
    messages = [SystemMessage(content=system_message)] + state.get("researcher_messages", []) + [HumanMessage(content=human_message)]
    response = config.llm.invoke(messages)
    
    # Extract raw notes from tool and AI messages
    raw_notes = [
        str(m.content) for m in filter_messages(
            state["researcher_messages"], 
            include_types=["tool", "ai"]
        )
    ]
    
    return {
        "compressed_research": str(response.content),
        "raw_notes": ["\n".join(raw_notes)]
    }

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Determine whether to continue research or provide final answer.
    
    Determines whether the agent should continue the research loop or provide
    a final answer based on whether the LLM made tool calls.
    
    Returns:
        "tool_node": Continue to tool execution
        "compress_research": Stop and compress research
    """
    messages = state["researcher_messages"]

    logger.debug(f"@func should_continue: Researcher messages: {messages}")
    last_message = messages[-1]

    # If the LLM makes a tool call, continue to tool execution
    if last_message.tool_calls:
        return "tool_node"
    # Otherwise, we have a final answer
    return "compress_research"


def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:
    """
    Determine if the user's request contains sufficient information to proceed with research.

    Uses structured output to make deterministic decisions and avoid hallucination.
    Routes to either research brief generation or ends with a clarification question.
    """
    # Set up structured output model
    structured_output_model = model.with_structured_output(ClarifyWithUser)

    # Invoke the model with clarification instructions
    response = structured_output_model.invoke([
        HumanMessage(content=CLARIFY_WITH_USER_MESSAGE.format(
            messages=get_buffer_string(messages=state["messages"]), 
            date=get_today_str()
        ))
    ])

    # Route based on clarification need
    if response.need_clarification:
        return Command(
            goto=END, 
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        return Command(
            goto="write_research_brief", 
            update={"messages": [AIMessage(content=response.verification)]}
        )

def write_research_brief(state: AgentState):
    """
    Transform the conversation history into a comprehensive research brief.

    Uses structured output to ensure the brief follows the required format
    and contains all necessary details for effective research.
    """
    # Set up structured output model
    structured_output_model = model.with_structured_output(ResearchQuestion)

    # Generate research brief from conversation history
    response = structured_output_model.invoke([
        HumanMessage(content=TRANSFORM_MESSAGES_INTO_RESEARCH_TOPIC_MESSAGE.format(
            messages=get_buffer_string(state.get("messages", [])),
            date=get_today_str()
        ))
    ])

    # Update state with generated research brief and pass it to the supervisor
    return {
        "research_brief": response.research_brief,
        "supervisor_messages": [HumanMessage(content=f"{response.research_brief}.")]
    }
