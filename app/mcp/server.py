import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Ensure the root project dir is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.orchestrator import CreationOrchestrator
from app.config import Config

# Initialize FastMCP Server
mcp = FastMCP("CreationManager")

@mcp.tool()
def run_creation_pipeline() -> str:
    """
    Executes the entire CreationManager multi-agent planning pipeline.
    This reads raw feedback, clusters & prioritizes insights, generates briefs,
    reviews them, and writes the output files to disk.
    """
    try:
        orchestrator = CreationOrchestrator()
        result = orchestrator.run_pipeline()
        if result.get("status") == "success":
            meta = result["metadata"]
            return f"Success! Processed {meta['total_feedback_items']} items, created {meta['briefs_created']} brief(s). Outputs saved in {Config.OUTPUT_DIR}"
        else:
            return "Pipeline ran but no briefs were created."
    except Exception as e:
        return f"Pipeline failed with error: {str(e)}"

@mcp.tool()
def get_latest_run_summary() -> str:
    """
    Retrieves the summary of the latest pipeline execution from metadata.
    """
    meta_path = Config.OUTPUT_DIR / "pipeline_run_metadata.json"
    if not meta_path.exists():
        return "No pipeline run metadata found. Please run the pipeline first."
    
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            import json
            data = json.load(f)
        return (
            f"Latest Pipeline Run Metadata:\n"
            f"- Total Ingested Items: {data.get('total_feedback_items')}\n"
            f"- Total Insights Extracted: {data.get('total_insights')}\n"
            f"- Briefs Created: {data.get('briefs_created')}\n"
            f"- Outputs Generated: {len(data.get('outputs', []))} files"
        )
    except Exception as e:
        return f"Failed to read run summary: {str(e)}"

if __name__ == "__main__":
    # Start the FastMCP server
    mcp.run()
