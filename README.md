# Neo4j Knowledge Graph Toolkit

A Python toolkit (work in progress) for semantic mapping and querying of medical terminology using Neo4j graph databases, specifically designed for working with caDSR (Cancer Data Standards Repository) and NCIT (NCI Thesaurus) data.

## Overview

This toolkit provides a modular foundation for automated semantic search and mapping across NCI's semantic infrastructure content. It enables mapping of raw medical data values to standardized NCIT terms and codes through exact matching, synonym finding, and AI-powered semantic analysis.

## Related Project

This toolkit is part of the broader [SI Tamer](https://github.com/CBIIT/si-tamer) ecosystem - a developing set of Retrieval Augmented Generation (RAG) tools for querying custom graph-based vector stores that aggregate data from caDSR and NCIT.

## Features

- **Exact Term Matching**: Find precise matches for NCIT codes and term names
- **Synonym Discovery**: Locate synonyms for permissible values and NCIT codes
- **Semantic Search with Embeddings**: Search embedding based semantic matches for permissible values and NCIT terms
- **LangChain and LLM Integration**: AI-powered semantic mapping using OpenAI models used as an Agent
- **Modular Architecture**: Separate tools for different types of queries
- **Environment-based Configuration**: Secure credential management
- **Streamlit Interface**: Run interactive demos or prototype visual workflows (new release)
- **Python Package Architecture**: Fully installable with pip install -e . for local use

## Project Structure

```
kg-toolkit/
├── src/
│   └── kg_toolkit/
│       ├── __init__.py
│       ├── pages/                     # Streamlit UI pages
│       ├── utils/                     # Common data handling utilities
│       ├── exact_match.py             # Exact node matching
│       ├── semantic_retrievers.py     # Embedding-based retrieval
│       ├── synonym_tool.py            # Synonym search logic
│       ├── llm_agent_4o.py            # AI mapping agent using LangChain
│       ├── streamlit_multipage_app.py # Interactive Streamlit app
│       └── tests/
├── pyproject.toml
├── requirements.txt
├── README.md
├── schema.png
└── .gitignore

```

## Core Components

### `exact_match.py`
Provides exact matching capabilities for NCIT nodes in the knowledge graph.

**Key Features:**
- Match nodes by NCIT code (e.g., "C4878")
- Match nodes by exact term name (e.g., "Lung Carcinoma")
- Retrieve comprehensive node information including definitions and embeddings
- Pattern-based partial searching

**Main Classes:**
- `get_node_match`: Primary class for exact node matching operations

### `synonym_tool.py` 
Handles synonym discovery for permissible values and NCIT concepts.

**Key Features:**
- Find synonyms for permissible values (PV → NCIT → SYN path)
- Find synonyms using NCIT codes (NCIT → SYN relationship)
- Support for both term-based and code-based synonym searches

**Main Classes:**
- `get_synonyms`: Primary class for synonym finding operations

### `semantic_retrievers.py`
Provides semantic matching capabilities for NCIT nodes and PV nodes in the knowledge graph.
This logic is inspired by the original [SI Tamer](https://github.com/CBIIT/si-tamer) toolset. 

**Key Features:**
- Turn PV or NCIT term into openAI embedding
- Match nodes by similarity search using embeddings metadata against the input embedding 
- Match nodes using definitions 
- Retrieve comprehensive node information including all metadata
- Rank results based on similarity scores


**Main Classes:**
- `SemanticSearcher`: Primary class for semantic matching operations for both PVs and NCIT terms

### `llm_agent.py`
LangChain-powered intelligent agent for semantic mapping with AI reasoning.

**Key Features:**
- Multi-tool orchestration for comprehensive semantic mapping
- OpenAI GPT-4o integration for intelligent decision making
- Structured output with confidence levels and reasoning
- Environment-based credential management


**Tool Classes:**
- `SynonymFinderTool`: LangChain wrapper for synonym finding
- `SynonymByCodeTool`: Code-based synonym discovery
- `NodeMatcherTool`: Exact node matching by NCIT code
- `TermMatcherTool`: Exact node matching by term name
- `SemanticPVSearchTool`: Semantic search using PV embedding
- `SemanticNCITSearchTool`: Semantic search using NCIT term embedding
- `SemanticCDEDefinitionTool`: Semantic search for finding CDEs by searching definitions using semantic similarity. (new release)

### `streamlit_multipage_app.py`
Streamlit-based interactive demo interface for testing and visualization.

Run via:
```bash
streamlit run src/kg_toolkit/streamlit_multipage_app.py
```

## Database Schema

The toolkit works with a Neo4j graph database containing the following node types:

| Node Label | Description | Vector Index |
|------------|-------------|--------------|
| NCIT | NCI Thesaurus Concept | ncitIndex |
| PV | Permissible Value | pvIndex |
| SYN | NCI Metathesaurus Synonym | - |
| CDE | Common Data Element | cdeIndex |
| VDM | Value Domain | vdmIndex |

### Node Properties

| Property | Description |
|----------|-------------|
| `term` | Title, term, or value |
| `code` | ID within source terminology |
| `definition` | Definition text |
| `openai_embedding` | Vector embedding of definition |
| `type` | Node classification |

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd kg-toolkit
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
   ```


3. **Install the package locally:**
   ```bash
    pip install -e .
   ```
This makes the package available for import:
```bash
   from kg_toolkit.semantic_retrievers import SemanticRetriever
```


## Configuration

Set the following environment variables:

```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-openai-api-key"

# Neo4j Configuration  
export NEO4J_URI="bolt://your-neo4j-server:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your-password"
```

**Windows:**
```cmd
setx OPENAI_API_KEY "your-openai-api-key"
setx NEO4J_URI "bolt://your-neo4j-server:7687"
setx NEO4J_USERNAME "neo4j"
setx NEO4J_PASSWORD "your-password"
```

## Usage example

### Connection Test
```bash
python tests/connection_test.py
```

### Individual Tool Tests
```bash
python tests/test_synonyms.py
python tests/test_exact_match.py
```

### Run Streamlit App
```bash
streamlit run src/kg_toolkit/streamlit_multipage_app.py
```

### Run Agent
```bash
python src/kg_toolkit/llm_agent_4o.py
```

### Import in Python
```bash
from kg_toolkit.synonym_tool import SynonymFinder
from kg_toolkit.semantic_retrievers import SemanticSearcher
```

## Related Resources

- [SI Tamer Main Repository](https://github.com/CBIIT/si-tamer)
- [caDSR (Cancer Data Standards Repository)](https://cadsr.cancer.gov)
- [NCI Thesaurus (NCIT)](https://evsexplore.semantics.cancer.gov)
- [LangChain Documentation](https://python.langchain.com)
- [Neo4j Documentation](https://neo4j.com/docs/)

