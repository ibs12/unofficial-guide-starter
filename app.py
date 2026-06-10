"""
Query interface for The Unofficial Guide (NYU off-campus housing RAG system).

Run with: python3 app.py
Then open http://localhost:7860
"""

import gradio as gr

from generate import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — NYU Off-Campus Housing") as demo:
    gr.Markdown(
        "# The Unofficial Guide — NYU Off-Campus Housing\n"
        "Ask a question about off-campus housing in NYC — apartment hunting, "
        "neighborhoods, leases, scams, and more — drawn from real Reddit "
        "discussions and official NYU/NYC housing resources. Answers are "
        "grounded only in retrieved documents and cite their sources below."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. What do commenters say about safety in Astoria?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=10)
    sources = gr.Textbox(label="Retrieved from", lines=6)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
