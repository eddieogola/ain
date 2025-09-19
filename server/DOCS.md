# African Insights Navigator (AIN) - Technical Documentation

## Overview

The African Insights Navigator (AIN) is a comprehensive AI-powered due diligence research platform specifically designed for African companies and markets. The system employs multiple specialized AI agents to conduct thorough research across finance, legal, governance, reputation, and risk dimensions using a multi-agent architecture built with LangGraph and LangChain.

## Architecture

### Core Components

- **Backend**: FastAPI-based server with multi-agent research system
- **Frontend**: Streamlit-based interactive chat interface
- **Infrastructure**: Docker containerization with multi-service architecture
- **AI Framework**: LangGraph for workflow orchestration, LangChain for LLM integration

## Module Documentation

### 1. Configuration Module (`src/config.py`)

**Purpose**: Central configuration management for the entire application.

**Key Components**:

- **Environment Detection**: Determines production vs development mode
- **API Key Management**: Handles Tavily and LLM API keys
- **Model Configuration**: Configures LLM parameters and base URLs
- **Client Initialization**: Sets up Tavily web search client and LLM instances
- **Memory Configuration**: Initializes short-term memory system

**Key Classes**:

- `Config`: Main configuration class that initializes all services
  - `web_search_client`: TavilyClient for web searches
  - `llm`: Primary language model instance
  - `writer_llm`: Specialized LLM for report writing
  - `short_term_memory`: Memory management system
  - `max_chunk_size`: Text processing chunk size (1000 chars)

**Functions**:

- `get_config()`: Cached factory function returning singleton Config instance

### 2. Agent System (`src/agents/`)

#### 2.1 Main Agent Orchestrator (`src/agents/main.py`)

**Purpose**: Orchestrates the complete research workflow from user input to final report.

**Key Components**:

- **Workflow States**: Manages research state transitions
- **Graph Construction**: Builds LangGraph workflow with multiple nodes
- **Report Generation**: Final synthesis of all agent findings

**Workflow Nodes**:

1. `clarify_with_user`: User clarification and scope definition
2. `write_research_brief`: Research brief generation
3. `supervisor_subgraph`: Multi-agent research coordination
4. `final_report_generation`: Consolidates findings into comprehensive report

#### 2.2 Supervisor Agent (`src/agents/supervisor.py`)

**Purpose**: Coordinates multiple specialized research agents and manages their execution.

**Key Responsibilities**:

- **Agent Coordination**: Manages parallel execution of specialized agents
- **Workflow Management**: Controls research iteration limits (max 24)
- **Task Distribution**: Assigns research tasks to appropriate agents
- **Result Aggregation**: Collects and organizes findings from all agents

#### 2.3 Common Agent Functions (`src/agents/common.py`)

**Purpose**: Shared functionality across all agents.

**Key Functions**:

- `clarify_with_user`: Handles user clarification requests
- `write_research_brief`: Generates structured research objectives

### 3. Specialized Research Agents

#### 3.1 Governance Agent

**Purpose**: Corporate structure, board composition, ESG performance analysis

- Analyzes corporate governance structures
- Evaluates board composition and leadership
- Assesses ESG (Environmental, Social, Governance) performance
- Reviews policies and compliance frameworks

#### 3.2 Finance Agent

**Purpose**: Financial analysis and fraud detection

- Financial statement analysis and interpretation
- Valuation support and financial modeling
- Fraud detection pattern identification
- Liquidity and solvency assessment

#### 3.3 Legal Agent

**Purpose**: Legal compliance and contract analysis

- Contract review and summarization
- Litigation and compliance status checks
- Intellectual property verification
- Permit and licensing verification

#### 3.4 Reputation Agent

**Purpose**: Media screening and sentiment analysis

- Adverse media screening and monitoring
- Sanctions and PEP (Politically Exposed Persons) screening
- Social sentiment analysis across platforms
- Stakeholder influence mapping

#### 3.5 Risk Agent

**Purpose**: Comprehensive risk assessment

- Geopolitical and macroeconomic risk evaluation
- Operational risk identification and assessment
- Cybersecurity risk indicators analysis
- Supply chain vulnerability assessment

### 4. Memory Management (`src/memory/`)

#### 4.1 State Management (`src/memory/state.py`)

**Purpose**: Defines data structures for agent state and workflow management.

**Key Classes**:

- `ClarifyWithUser`: Schema for user clarification decisions

  - `need_clarification`: Boolean flag for clarification needs
  - `question`: Clarifying question to ask user
  - `verification`: Confirmation message for research start

- `ResearchQuestion`: Schema for research brief generation

  - `research_brief`: Structured research question for guidance

- `AgentState`: Main state container for the research workflow
- `AgentInputState`: Input schema for user requests

#### 4.2 Short-term Memory (`src/memory/short_term.py`)

**Purpose**: Manages conversation memory and context retention.

- Maintains conversation history
- Provides context for agent interactions
- Manages memory persistence across research sessions

### 5. Tools System (`src/tools/`)

#### 5.1 Search Tools (`src/tools/search.py`)

**Purpose**: Web search and information retrieval capabilities.

**Key Functions**:

- `tavily_search`: Primary web search function using Tavily API
- Search result processing and filtering
- Content extraction and summarization
- Source citation management

#### 5.2 Strategic Thinking Tools

**Purpose**: Strategic reflection and planning capabilities for agents.

- Provides agents with strategic thinking capabilities
- Enables planning and reflection on research approaches
- Supports decision-making processes

### 6. Prompt Engineering (`src/prompts/`)

#### 6.1 Agent Prompts (`src/prompts/agents.py`)

**Purpose**: System prompts for all research agents.

**Key Prompts**:

- `FINAL_REPORT_GENERATION_SYSTEM_MESSAGE`: Template for final report generation
- Agent-specific system prompts for each specialized agent
- Citation and source formatting rules
- Report structure guidelines

**Citation Rules**:

- Sequential citation numbering (1, 2, 3, 4...)
- Source listing with URLs
- Inline citations throughout reports

#### 6.2 Search Prompts (`src/prompts/search.py`)

**Purpose**: Prompts for web content processing and summarization.

**Key Prompts**:

- `SUMMARIZE_WEBPAGE`: Comprehensive webpage summarization template
- Content type-specific handling (news, scientific, opinion, product pages)
- Key information preservation guidelines
- Output formatting standards

**Content Processing Guidelines**:

- Preserve main topics and key facts
- Maintain chronological order for time-sensitive content
- Keep important quotes and statistics
- Aim for 25-30% of original length

### 7. API Layer (`src/routes/`)

**Purpose**: RESTful API endpoints for client communication.

**Key Endpoints**:

- `POST /api/v1/research`: Main research endpoint
- `GET /api/v1/healthz`: Health check endpoint

**Request/Response Format**:

```json
{
  "message": "Research request text",
  "code": 200,
  "status": "success",
  "data": {
    "final_report": "Comprehensive research report..."
  }
}
```

### 8. Utilities (`src/utils/`)

#### 8.1 Time Utilities (`src/utils/time.py`)

**Purpose**: Time-related helper functions.

- `get_today_str()`: Returns current date string for reports
- Date formatting for research timestamps

#### 8.2 Logging Utilities (`src/utils/logging.py`)

**Purpose**: Application logging and debugging support.

- Structured logging for agent activities
- Debug information for function calls
- Performance monitoring and troubleshooting

### 9. Frontend (`src/client.py`)

**Purpose**: Streamlit-based interactive user interface.

**Features**:

- Real-time chat interface for research requests
- WebSocket communication with backend
- Responsive design for various screen sizes
- Research progress tracking and display

### 10. Server (`src/server.py`)

**Purpose**: FastAPI application server and main entry point.

**Features**:

- RESTful API server implementation
- Request routing and handling
- CORS configuration
- Health monitoring endpoints
- Integration with agent system

## Dependencies

### Core Libraries

- **FastAPI**: Web framework and API server
- **LangChain**: LLM orchestration and tool integration
- **LangGraph**: Multi-agent workflow management
- **Streamlit**: Frontend user interface
- **Tavily**: Web search and research capabilities
- **Pydantic**: Data validation and schema management

### Supporting Libraries

- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing support
- **Pillow**: Image processing capabilities
- **GitPython**: Version control integration

## Configuration Requirements

### Environment Variables

```env
ENVIRONMENT=dev|prod
MODEL_BASE_URL=your_model_base_url
MODEL_NAME=gpt-4o
MODEL_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Performance Parameters

- **Tool Call Budgets**: 2-5 calls per agent to prevent excessive searching
- **Parallel Execution**: Up to 6 concurrent research agents
- **Iteration Limits**: Maximum 24 iterations per research session
- **Text Chunk Size**: 1000 characters for LLM processing

## Workflow Process

1. **User Input**: Research request received via Streamlit interface
2. **Clarification**: System clarifies scope and requirements if needed
3. **Research Brief**: Generates structured research objectives
4. **Agent Coordination**: Supervisor distributes tasks to specialized agents
5. **Parallel Research**: Multiple agents conduct concurrent research
6. **Information Gathering**: Agents use web search and strategic thinking tools
7. **Report Synthesis**: Final report generated consolidating all findings
8. **Delivery**: Comprehensive report delivered to user with citations

## Development and Testing

### Notebooks

- `notebooks/agents_v2.ipynb`: Agent testing and development
- `notebooks/search.ipynb`: Search functionality testing

### Docker Configuration

- Multi-service architecture with separate client and server containers
- Hot reload and file watching for development
- Health monitoring and auto-restart capabilities

This documentation provides a comprehensive overview of the AIN system architecture, module functionality, and operational workflows.
