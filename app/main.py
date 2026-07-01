import sys
from pathlib import Path

# Add project root to path if running directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.orchestrator import CreationOrchestrator

def main():
    try:
        orchestrator = CreationOrchestrator()
        result = orchestrator.run_pipeline()
        print("\nPipeline run result:")
        print(f"Status: {result.get('status')}")
        if result.get("status") == "success":
            meta = result.get("metadata", {})
            print(f"Processed {meta.get('total_feedback_items')} feedback items.")
            print(f"Generated {meta.get('briefs_created')} product briefs.")
            print("Done!")
    except Exception as e:
        print(f"Pipeline failed with error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
