"""
Grounded generation for The Unofficial Guide (NYU off-campus housing).

Connects retrieval (vector_store.retrieve) to Groq's llama-3.3-70b-versatile
to produce answers that are grounded ONLY in retrieved chunks — never the
model's general knowledge — with guaranteed source attribution.

Grounding is enforced two ways:
  1. A system prompt that explicitly restricts the model to the provided
     context, tells it to say so when the context is insufficient, and
     instructs it to surface — not adjudicate — disagreement between sources
     (per planning.md: this is "an unofficial guide," not an authority; the
     reader should weigh conflicting opinions themselves).
  2. Source attribution is built programmatically from retrieval metadata
     and appended to every response — it does not depend on the model
     remembering to cite correctly.

Usage:
    from generate import ask
    result = ask("What do commenters say about Astoria vs Williamsburg?")
    print(result["answer"])
    print(result["sources"])
"""

import os

from dotenv import load_dotenv
from groq import Groq

from vector_store import retrieve, TOP_K

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are The Unofficial Guide — a grounded Q&A assistant over student- \
and renter-generated discussion (Reddit threads) and official NYU/NYC housing \
resources, focused on off-campus housing for NYU students in New York City.

STRICT GROUNDING RULES:
- Answer ONLY using the information in the "Retrieved context" below. Do not \
add facts, explanations, or advice from your own general knowledge — even if \
you believe it to be true or helpful.
- If the retrieved context does not contain enough information to answer the \
question, respond exactly: "I don't have enough information on that." Do not \
guess or fill the gap with general knowledge.
- This is an UNOFFICIAL guide built from opinionated, sometimes-conflicting \
sources. When retrieved chunks disagree, do not declare a winner or decide \
which opinion is "more correct." Instead, present each side and the signal \
that distinguishes them as written (e.g., one commenter states firsthand, \
lived experience with specific detail, while another gives an unsupported \
one-line opinion) — and let the reader weigh which to trust.
- Reference which source each claim comes from inline (e.g., "according to \
[source]..." or "one commenter in [source] says...").
"""

USER_PROMPT_TEMPLATE = """Question: {question}

Retrieved context:
{context}

Answer the question using only the retrieved context above, following the \
grounding rules in your instructions."""


def _format_context(chunks: list[dict]) -> str:
    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        blocks.append(f"[{i}] Source: {chunk['source']}\n{chunk['text']}")
    return "\n\n".join(blocks)


def _format_sources(chunks: list[dict]) -> list[str]:
    """Build the guaranteed source-attribution list from retrieval metadata directly —
    not from the model's response, so attribution can't be dropped or hallucinated."""
    seen = []
    for chunk in chunks:
        label = f"{chunk['source']} (chunk {chunk['chunk_index']})"
        if label not in seen:
            seen.append(label)
    return seen


def generate_answer(question: str, chunks: list[dict]) -> str:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                question=question,
                context=_format_context(chunks),
            )},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def ask(question: str, k: int = TOP_K) -> dict:
    """End-to-end: retrieve relevant chunks, generate a grounded answer, attach sources.

    Returns {"answer": str, "sources": list[str], "chunks": list[dict]}
    """
    chunks = retrieve(question, k=k)
    answer = generate_answer(question, chunks)
    return {
        "answer": answer,
        "sources": _format_sources(chunks),
        "chunks": chunks,
    }


SAMPLE_QUERIES = [
    "What do commenters say about the trade-offs of living in Astoria versus Williamsburg?",
    "What does the NYU Lease Guarantor article say a student needs without a US-based co-signer?",
    "What is the best pizza place near NYU?",  # out-of-scope — should decline
]


if __name__ == "__main__":
    for query in SAMPLE_QUERIES:
        result = ask(query)
        print(f"\n{'=' * 70}\nQuery: {query}\n{'-' * 70}")
        print(f"Answer:\n{result['answer']}\n")
        print("Sources:")
        for s in result["sources"]:
            print(f"  • {s}")
