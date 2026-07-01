import pandas as pd
from pathlib import Path
from typing import List
from app.models import FeedbackItem
from app.tools.cleaning import clean_text, remove_pii

class IngestionAgent:
    """
    IngestionAgent reads raw data from multiple files, runs basic PII redaction and text cleaning,
    and returns a structured list of FeedbackItems.
    """
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def ingest_all(self) -> List[FeedbackItem]:
        feedback_items = []
        
        # 1. Ingest Comments CSV (includes likes/engagement signals)
        csv_path = self.data_dir / "sample_comments.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            for idx, row in df.iterrows():
                content = clean_text(remove_pii(str(row.get('comment', ''))))
                likes = int(row.get('likes', 0))
                feedback_items.append(FeedbackItem(
                    id=f"comment_{idx}",
                    source="comments",
                    content=content,
                    likes=likes,
                    metadata={"user": row.get('user', 'anonymous')}
                ))
                
        # 2. Ingest Notes MD
        notes_path = self.data_dir / "sample_notes.md"
        if notes_path.exists():
            with open(notes_path, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned_content = clean_text(remove_pii(content))
            
            # Create a feedback item for notes
            feedback_items.append(FeedbackItem(
                id="notes_1",
                source="notes",
                content=cleaned_content
            ))
            
        # 3. Ingest Transcripts TXT
        transcript_path = self.data_dir / "sample_transcripts.txt"
        if transcript_path.exists():
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned_content = clean_text(remove_pii(content))
            feedback_items.append(FeedbackItem(
                id="transcript_1",
                source="transcript",
                content=cleaned_content
            ))
            
        return feedback_items
