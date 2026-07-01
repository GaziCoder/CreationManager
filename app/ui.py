import os
import sys
from pathlib import Path
import gradio as pd_gr  # using alias to make sure it's clear
import gradio as gr

# Ensure the root project dir is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.config import Config
from app.orchestrator import CreationOrchestrator

def run_agent_pipeline(api_key, model_name, pasted_text, uploaded_file):
    # Update Config dynamically
    if api_key:
        Config.GEMINI_API_KEY = api_key.strip()
    if model_name:
        Config.GEMINI_MODEL = model_name
        
    # Handle pasted text
    if pasted_text and pasted_text.strip():
        pasted_path = Config.DATA_DIR / "pasted_comments.csv"
        # If it doesn't look like CSV, we can write a simple CSV row or write to transcript
        if "," not in pasted_text:
            # write as comments csv format
            with open(pasted_path, "w", encoding="utf-8") as f:
                f.write("comment,user,likes\n")
                f.write(f'"{pasted_text.strip().replace(chr(34), chr(39))}",pasted_user,10\n')
        else:
            with open(pasted_path, "w", encoding="utf-8") as f:
                f.write(pasted_text.strip())

    # Handle uploaded file
    if uploaded_file is not None:
        file_path = Path(uploaded_file.name)
        destination = Config.DATA_DIR / file_path.name
        with open(destination, "wb") as f:
            f.write(open(file_path, "rb").read())
            
    # Run orchestrator
    try:
        orchestrator = CreationOrchestrator()
        result = orchestrator.run_pipeline()
        
        if result.get("status") != "success":
            return "### Pipeline Execution Completed, but no briefs were generated.", ""
            
        meta = result.get("metadata", {})
        summary_md = f"""
        ### ✅ Pipeline Success!
        * **Total Feedback Items Ingested:** {meta.get('total_feedback_items')}
        * **Total Theme Insights Extracted:** {meta.get('total_insights')}
        * **Approved Content Briefs Generated:** {meta.get('briefs_created')}
        """
        
        # Read the generated briefs
        briefs_output_md = ""
        for brief_path_str in meta.get("outputs", []):
            brief_path = Path(brief_path_str)
            if brief_path.exists():
                with open(brief_path, "r", encoding="utf-8") as f:
                    content = f.read()
                briefs_output_md += f"\n\n---\n\n{content}"
                
        return summary_md, briefs_output_md
        
    except Exception as e:
        return f"### ❌ Pipeline Execution Failed\n**Error:** {str(e)}", ""

# Design CSS for custom premium styling
custom_css = """
body {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Outfit', 'Inter', sans-serif;
}
.gradio-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
    border-radius: 16px;
    padding: 30px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}
button.primary {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.HTML(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #c084fc; font-weight: 800; font-size: 2.5rem; margin-bottom: 5px;">🔮 CreationManager</h1>
            <p style="color: #94a3b8; font-size: 1.1rem;">Multi-Agent Planner: Turn Audience Feedback into Ranked, Evidence-Backed Content Decisions</p>
        </div>
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Pipeline Configuration")
            api_key_input = gr.Textbox(
                label="Gemini API Key", 
                placeholder="Enter your GEMINI_API_KEY (leave empty to use .env key)",
                type="password"
            )
            model_input = gr.Dropdown(
                choices=["gemini-2.5-flash", "gemini-2.5-pro"],
                value="gemini-2.5-flash",
                label="Gemini Model"
            )
            
            gr.Markdown("### 📥 Input Feedback Source")
            pasted_input = gr.Textbox(
                label="Paste Comments / Feedback",
                placeholder="Example: Can you do a tutorial on custom MCP servers?,user1,15",
                lines=5
            )
            file_input = gr.File(
                label="Upload Feedback File (CSV/MD/TXT)"
            )
            
            run_btn = gr.Button("🚀 Run Multi-Agent Planning Pipeline", variant="primary", elem_classes="primary")
            
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Pipeline Results Summary")
            summary_output = gr.Markdown("Submit configuration and inputs to execute the agents.")
            
            gr.Markdown("### 📑 Generated Decision Briefs")
            briefs_output = gr.Markdown("Your ranked, evidence-backed Content Briefs will appear here.")
            
    run_btn.click(
        fn=run_agent_pipeline,
        inputs=[api_key_input, model_input, pasted_input, file_input],
        outputs=[summary_output, briefs_output]
    )

if __name__ == "__main__":
    # Launch on local server
    demo.launch(server_name="127.0.0.1", server_port=7860)
