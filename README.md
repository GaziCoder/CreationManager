# CreationManager

CreationManager is a multi-agent system designed to ingest, process, cluster, score, and transform raw user feedback, comments, notes, and transcripts into comprehensive, prioritized product planning briefs.

## Project Structure

```text
CreationManager/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── main.py
│   ├── orchestrator.py
│   ├── config.py
│   ├── models.py
│   ├── agents/
│   │   ├── ingestion_agent.py
│   │   ├── insight_agent.py
│   │   ├── prioritization_agent.py
│   │   ├── planning_agent.py
│   │   └── review_agent.py
│   ├── tools/
│   │   ├── cleaning.py
│   │   ├── clustering.py
│   │   ├── scoring.py
│   │   ├── briefs.py
│   │   └── security.py
│   └── mcp/
│       └── server.py
├── data/
│   ├── sample_comments.csv
│   ├── sample_notes.md
│   └── sample_transcripts.txt
└── outputs/
```

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your LLM provider credentials and configurations
   ```

3. Run the orchestration pipeline:
   ```bash
   python app/main.py
   ```
