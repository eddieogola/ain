# African Insights Navigator (AIN)

A comprehensive AI-powered due diligence research platform specifically designed for African companies and markets. The system employs multiple specialized AI agents to conduct thorough research across finance, legal, governance, reputation, and risk dimensions.

## 🌟 Features

### Multi-Agent Research System

- **Governance Agent**: Corporate structure, board composition, ESG performance
- **Finance Agent**: Financial statement analysis, valuation support, fraud detection
- **Legal Agent**: Contract review, litigation checks, IP verification, compliance
- **Reputation Agent**: Media screening, sentiment analysis, stakeholder mapping
- **Risk Agent**: Geopolitical risks, operational vulnerabilities, cybersecurity indicators
- **Supervisor Agent**: Coordinates research activities and manages agent workflows

### Core Capabilities

- **Automated Due Diligence**: Comprehensive company research and analysis
- **Real-time Web Research**: Integration with Tavily for current information
- **Interactive Chat Interface**: Streamlit-based user interface
- **Parallel Processing**: Multiple agents work concurrently for efficiency
- **Comprehensive Reporting**: Detailed final reports with citations and sources

## 🏗️ Architecture

### Backend (FastAPI)

- **Multi-agent system** using LangGraph for workflow orchestration
- **Modular agent design** with specialized research capabilities
- **Tool-based architecture** with web search and strategic thinking tools
- **Memory management** with short-term and checkpointing support
- **RESTful API** for client communication

### Frontend (Streamlit)

- **Interactive chat interface** for research requests
- **Real-time communication** with backend agents
- **Responsive design** for various screen sizes

### Infrastructure

- **Docker containerization** for easy deployment
- **Multi-service architecture** with separate client and server containers
- **Health monitoring** and auto-restart capabilities
- **Development workflow** with hot reload and file watching

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Environment variables configured (see Environment Setup)

### Environment Setup

Create a `.env` file in the `/server` directory with:

```env
# Core Configuration
ENVIRONMENT=dev  # or 'prod' for production

# AI Model Configuration
MODEL_BASE_URL=your_model_base_url
MODEL_NAME=gpt-4o  # or your preferred model
MODEL_API_KEY=your_openai_api_key

# Research Tools
TAVILY_API_KEY=your_tavily_api_key
```

### Running the Application

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ain
   ```

2. **Start the services**

   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - **Client Interface**: http://localhost:8501
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/v1/healthz

## 📡 API Endpoints

### Research Endpoint

```http
POST /api/v1/research
Content-Type: application/json

{
  "message": "Research Safaricom PLC Kenyan company"
}
```

**Response:**

```json
{
  "code": 200,
  "status": "success",
  "message": null,
  "data": {
    "final_report": "Comprehensive research report..."
  }
}
```

### Health Check

```http
GET /api/v1/healthz
```

## 🤖 Agent System

### Research Workflow

1. **User Clarification**: System clarifies research scope and requirements
2. **Research Brief Generation**: Creates detailed research objectives
3. **Multi-Agent Research**: Parallel execution across specialized agents
4. **Report Synthesis**: Consolidates findings into comprehensive report

### Agent Specializations

#### Governance Agent

- Corporate structure analysis
- Board and leadership assessment
- Policy and compliance review
- ESG performance evaluation

#### Finance Agent

- Financial statement analysis
- Valuation support and modeling
- Fraud detection patterns
- Liquidity and solvency assessment

#### Legal Agent

- Contract review and summarization
- Litigation and compliance checks
- Intellectual property verification
- Permit and licensing verification

#### Reputation Agent

- Adverse media screening
- Sanctions and PEP screening
- Social sentiment analysis
- Stakeholder influence mapping

#### Risk Agent

- Geopolitical and macroeconomic risks
- Operational risk identification
- Cybersecurity risk indicators
- Supply chain vulnerabilities

## 🛠️ Development

### Project Structure

```
ain/
├── server/
│   ├── src/
│   │   ├── agents/           # Agent implementations
│   │   ├── config.py         # Configuration management
│   │   ├── routes/           # API routes
│   │   ├── prompts/          # Agent system prompts
│   │   ├── tools/            # Research and utility tools
│   │   ├── utils/            # Helper utilities
│   │   ├── memory/           # State and memory management
│   │   ├── client.py         # Streamlit frontend
│   │   └── server.py         # FastAPI application
│   ├── notebooks/            # Development notebooks
│   ├── requirements.*.txt    # Dependencies
│   └── Dockerfile.*         # Container definitions
└── docker-compose.yml       # Service orchestration
```

### Running Development Environment

```bash
# Start with file watching for development
docker-compose up --build

# View logs
docker-compose logs -f server
docker-compose logs -f client
```

### Testing Agents

Use the Jupyter notebook at `server/notebooks/agents_v2.ipynb` to test individual agents and workflows.

## 🔧 Configuration

### Model Configuration

The system supports various LLM providers through LangChain's `init_chat_model`:

- OpenAI (default)
- Ollama (local models)
- Other LangChain-supported providers

### Research Tools

- **Tavily**: Web search and research capabilities
- **Think Tool**: Strategic reflection and planning
- **Memory**: Short-term conversation memory

### Performance Tuning

- **Tool Call Budgets**: Prevents excessive searching (2-5 calls per agent)
- **Parallel Execution**: Up to 6 concurrent research agents
- **Iteration Limits**: Maximum 24 iterations per research session

## 📚 Dependencies

### Core Libraries

- **FastAPI**: Web framework and API
- **LangChain**: LLM orchestration and tools
- **LangGraph**: Multi-agent workflow management
- **Streamlit**: Frontend interface
- **Tavily**: Web search integration
- **Pydantic**: Data validation and settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the provided notebooks
5. Submit a pull request

## 📄 License

[License information to be added]

## 🆘 Support

For questions, issues, or contributions, please [create an issue](link-to-issues) or contact the development team.

---

**Built for African markets with AI-powered insights** 🌍
