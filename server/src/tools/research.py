"""Tools for research tasks."""

from typing import Annotated

from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command
from pydantic import BaseModel

from utils.logging import logger

@tool
class ResearchComplete(BaseModel):
    """Tool for indicating that the research process is complete."""
    pass

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    """
    Handoff tool to transfer control to another agent.
    Args:
        agent_name (str): The name of the agent to transfer control to.
        description (str | None): Optional description for the tool. Defaults to "Ask {agent_name} for help."
    Returns:
        A tool function that, when called, returns a Command to transfer control to the specified agent
    """
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help in researching the company given the research_topic."

    @tool(name, description=description)
    def handoff_tool(
        research_topic: str,
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Transfers control to another agent.
        This function is used to delegate tasks to specialized agents by transferring the current state

        transfer_to_<agent_name> tool call.

        Args:
            research_topic (str): The research topic being investigated.

        Returns:
            Command: A command to transfer control to the specified agent with the current state.
        
        """
        
        logger.debug(f"@func handoff_tool: Transferring to {agent_name} with tool_call_id {tool_call_id}\n State: {state}")
    
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,  
            update={**state, "messages": state["messages"] + [tool_message], "research_topic": research_topic},  
            graph=Command.PARENT,  
        )

    return handoff_tool