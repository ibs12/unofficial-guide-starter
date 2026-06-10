"""
Query interface for The Unofficial Guide (NYU off-campus housing RAG system).

Run with: python3 app.py
Then open http://localhost:7860
"""

import gradio as gr

from generate import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    chunks = "\n\n---\n\n".join(
        f"**{c['source']} (chunk {c['chunk_index']}, distance {c['distance']:.3f})**\n\n{c['text']}"
        for c in result["chunks"]
    )
    return result["answer"], sources, chunks


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
    with gr.Accordion("Retrieved chunks (full text)", open=False):
        chunks_display = gr.Markdown()

    btn.click(handle_query, inputs=inp, outputs=[answer, sources, chunks_display])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources, chunks_display])

if __name__ == "__main__":
    demo.launch()
