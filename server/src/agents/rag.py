from langgraph.prebuilt import create_react_agent
from tools.rag import retrieve_context
from config import get_config

config = get_config()
llm = config.llm

tools = [retrieve_context]
# If desired, specify custom instructions
prompt = (
    "You have access to a tool that retrieves context from a document. "
    "Use the tool to help answer user queries."
)

agent = create_react_agent(llm, tools, prompt=prompt)