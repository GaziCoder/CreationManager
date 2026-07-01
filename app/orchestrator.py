import json
from pathlib import Path
from typing import List, Dict, Any
from app.config import Config
from app.models import ProductBrief
from app.agents.ingestion_agent import IngestionAgent
from app.agents.insight_agent import InsightAgent
from app.agents.prioritization_agent import PrioritizationAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.review_agent import ReviewAgent
from app.tools.briefs import format_brief_to_markdown

class CreationOrchestrator:
    """
    CreationOrchestrator orchestrates the multi-agent feedback processing pipeline.
    It triggers each agent sequentially and writes the final brief reports to the outputs directory.
    """
    def __init__(self):
        # Retrieve key and model configurations
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.data_dir = Config.DATA_DIR
        self.output_dir = Config.OUTPUT_DIR
        
        # Instantiate agents
        self.ingestion_agent = IngestionAgent(data_dir=self.data_dir)
        self.insight_agent = InsightAgent(api_key=self.api_key, model_name=self.model_name)
        self.prioritization_agent = PrioritizationAgent(api_key=self.api_key, model_name=self.model_name)
        self.planning_agent = PlanningAgent(api_key=self.api_key, model_name=self.model_name)
        self.review_agent = ReviewAgent(api_key=self.api_key, model_name=self.model_name)

    def run_pipeline(self) -> Dict[str, Any]:
        print("Starting CreationManager Multi-Agent Pipeline...")
        
        # Step 1: Ingestion
        print("[1/5] Ingesting feedback data...")
        feedback_items = self.ingestion_agent.ingest_all()
        print(f"Ingested {len(feedback_items)} feedback items.")
        
        if not feedback_items:
            print("No feedback items found. Pipeline stopping.")
            return {"status": "empty", "briefs_created": 0}
            
        # Step 2: Insights Extraction
        print("[2/5] Synthesizing insights...")
        insights = self.insight_agent.extract_insights(feedback_items)
        print(f"Extracted {len(insights)} insights.")
        
        # Step 3: Prioritization
        print("[3/5] Scoring and prioritizing insights...")
        prioritized_insights = self.prioritization_agent.prioritize(insights)
        
        # Step 4: Planning
        print("[4/5] Constructing product briefs...")
        briefs = self.planning_agent.create_briefs(prioritized_insights)
        
        # Step 5: Review
        print("[5/5] Performing security and quality reviews...")
        reviewed_briefs: List[ProductBrief] = []
        for brief in briefs:
            reviewed_brief = self.review_agent.review(brief)
            reviewed_briefs.append(reviewed_brief)
            
        # Write Output files
        print(f"Pipeline complete. Writing {len(reviewed_briefs)} briefs to {self.output_dir}...")
        written_paths = []
        for brief in reviewed_briefs:
            markdown_content = format_brief_to_markdown(brief)
            file_name = f"{brief.id}_{brief.title.lower().replace(' ', '_').replace(':', '')}.md"
            out_path = self.output_dir / file_name
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            written_paths.append(str(out_path))
            
        # Write run metadata
        meta_path = self.output_dir / "pipeline_run_metadata.json"
        metadata = {
            "total_feedback_items": len(feedback_items),
            "total_insights": len(insights),
            "briefs_created": len(reviewed_briefs),
            "outputs": written_paths
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        return {
            "status": "success",
            "metadata": metadata,
            "briefs": [b.model_dump() for b in reviewed_briefs]
        }
