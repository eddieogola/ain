
"""
Tools for performing web searches using the Tavily search API with content summarization.
"""
from typing_extensions import Annotated, Literal
from langchain_core.tools import tool, InjectedToolArg
from utils.search import web_search_multiple, deduplicate_search_results, process_search_results, format_search_output
from utils.logging import logger

@tool(parse_docstring=True)
def web_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 3,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
) -> str:
    """Fetch results from Tavily search API with content summarization.

    Args:
        query: A single search query to execute
        max_results: Maximum number of results to return
        topic: Topic to filter results by ('general', 'news', 'finance')

    Returns:
        Formatted string of search results with summaries
    """

    # Execute search for single query
    logger.debug(f"@tool web_search for query: {query}, max_results: {max_results}, topic: {topic}")
    search_results = web_search_multiple(
        [query],  # Convert single query to list for the internal function
        max_results=max_results,
        topic=topic,
        include_raw_content=True,   
    )
    logger.debug(f"@tool web_search received {len(search_results[0]['results'])} results from Tavily\n\n")
    logger.debug(f"@tool web_search search_results: {search_results}\n\n")

    # Deduplicate results by URL to avoid processing duplicate content
    unique_results = deduplicate_search_results(search_results)

    logger.debug(f"@tool web_search deduplicated to {len(unique_results)} unique results\n\n")
    logger.debug(f"@tool web_search unique_results: {unique_results}\n\n")

    # Process results with summarization
    summarized_results = process_search_results(unique_results)

    # Format output for consumption
    formatted_search = format_search_output(summarized_results)
    logger.debug(f"@tool web_search completed: returning formatted results: {formatted_search}")

    return formatted_search
