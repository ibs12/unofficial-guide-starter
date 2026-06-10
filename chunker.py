"""
Comment-aware chunking for The Unofficial Guide (NYU off-campus housing).

Strategy (see planning.md "Chunking Strategy" for the full reasoning):
  - Target chunk size: ~200 tokens, measured with the same tokenizer as our
    embedding model (all-MiniLM-L6-v2, max_seq_length=256) so chunks never
    get silently truncated when embedded.
  - Reddit threads are split on their existing POST TITLE / POST BODY / COMMENT
    boundaries (one "thought" per block); NYU articles are split on paragraphs.
  - Consecutive short blocks are merged up to the ~200 token target so a chunk
    is never a lone 9-word fragment.
  - The rare block that *exceeds* the target on its own (e.g., a long detailed
    comment) is split into multiple chunks WITH overlap — overlap is applied
    only in this case, since merged-block chunks already contain complete
    thoughts and don't need redundant context at their edges.

Produces a flat list of chunk dicts:
    {"text": <chunk text>, "source": <filename>, "doc_type": ..., "chunk_index": <int>}
ready to be embedded and stored in ChromaDB with that metadata attached.
"""

import re

from transformers import AutoTokenizer

from ingest import load_documents

TARGET_TOKENS = 200
SPLIT_OVERLAP_TOKENS = 40  # ~20% of target — only used when a single block must be split

_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def _token_count(text: str) -> int:
    return len(_tokenizer.encode(text, add_special_tokens=False))


MIN_BLOCK_TOKENS = 30  # below this, a block reads as a fragment, not a complete thought


def _merge_tiny_blocks(blocks: list[str]) -> list[str]:
    """Fold any block under MIN_BLOCK_TOKENS into the following block.

    Lone "POST TITLE: ..." blocks (no body text, e.g. link posts) are the main
    case — a title alone isn't a self-contained thought, but "title + first
    comment" reads naturally as one. Falls back to merging backward for a tiny
    block at the very end of a document.
    """
    if not blocks:
        return blocks

    merged: list[str] = []
    pending = ""
    for block in blocks:
        combined = f"{pending}\n\n{block}" if pending else block
        if _token_count(combined) < MIN_BLOCK_TOKENS:
            pending = combined
        else:
            merged.append(combined)
            pending = ""

    if pending:
        if merged:
            merged[-1] = f"{merged[-1]}\n\n{pending}"
        else:
            merged.append(pending)

    return merged


def _split_into_blocks(doc: dict) -> list[str]:
    """Break a document into its natural 'one complete thought' units."""
    if doc["doc_type"] == "reddit":
        # Each POST TITLE / POST BODY / COMMENT is its own retrievable thought
        parts = re.split(r"\n\n(?=POST TITLE:|POST BODY:|COMMENT:)", doc["text"])
    else:
        # NYU articles: paragraphs separated by blank lines
        parts = re.split(r"\n\n+", doc["text"])
    blocks = [p.strip() for p in parts if p.strip()]
    return _merge_tiny_blocks(blocks)


def _split_long_block(block: str) -> list[str]:
    """Split a block that alone exceeds TARGET_TOKENS, with overlap between pieces.

    Slices the *original* string using the tokenizer's character offset mapping
    rather than decoding token ids back to text — decoding through a WordPiece
    tokenizer lowercases everything and inserts "##" continuation markers and
    spaced-out punctuation, which would produce unreadable, ungroundable chunks.
    """
    encoding = _tokenizer(block, add_special_tokens=False, return_offsets_mapping=True)
    offsets = encoding["offset_mapping"]

    pieces = []
    start = 0
    step = TARGET_TOKENS - SPLIT_OVERLAP_TOKENS
    while start < len(offsets):
        end = min(start + TARGET_TOKENS, len(offsets)) - 1
        char_start = offsets[start][0]
        char_end = offsets[end][1]
        pieces.append(block[char_start:char_end].strip())
        if start + TARGET_TOKENS >= len(offsets):
            break
        start += step
    return pieces


def chunk_document(doc: dict) -> list[dict]:
    """Apply the comment-aware merge/split strategy to a single document."""
    blocks = _split_into_blocks(doc)

    chunks = []
    current_parts: list[str] = []
    current_tokens = 0

    def flush():
        nonlocal current_parts, current_tokens
        if current_parts:
            chunks.append("\n\n".join(current_parts))
            current_parts = []
            current_tokens = 0

    for block in blocks:
        block_tokens = _token_count(block)

        if block_tokens > TARGET_TOKENS:
            # Long block: flush whatever we were building, then split this one on its own
            flush()
            chunks.extend(_split_long_block(block))
            continue

        if current_tokens + block_tokens > TARGET_TOKENS:
            flush()

        current_parts.append(block)
        current_tokens += block_tokens

    flush()

    return [
        {"text": text, "source": doc["source"], "doc_type": doc["doc_type"], "chunk_index": i}
        for i, text in enumerate(chunks)
    ]


def chunk_all_documents() -> list[dict]:
    all_chunks = []
    for doc in load_documents():
        all_chunks.extend(chunk_document(doc))
    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_documents()
    token_counts = [_token_count(c["text"]) for c in chunks]

    print(f"Total chunks: {len(chunks)}")
    print(f"Token count — min: {min(token_counts)}  median: {sorted(token_counts)[len(token_counts)//2]}  "
          f"mean: {sum(token_counts)//len(token_counts)}  max: {max(token_counts)}")
    over_limit = sum(1 for t in token_counts if t > 256)
    print(f"Chunks exceeding the 256-token embedding limit: {over_limit}")

    print("\n--- 5 representative chunks ---")
    # Pick a spread: shortest, a couple mid-range, and the longest, plus one NYU chunk
    by_tokens = sorted(range(len(chunks)), key=lambda i: token_counts[i])
    sample_indices = [
        by_tokens[0],
        by_tokens[len(by_tokens) // 4],
        by_tokens[len(by_tokens) // 2],
        by_tokens[(3 * len(by_tokens)) // 4],
        next(i for i in by_tokens[::-1] if chunks[i]["doc_type"] == "nyu_official"),
    ]
    for n, i in enumerate(sample_indices, 1):
        c = chunks[i]
        print(f"\n[{n}] source={c['source']}  doc_type={c['doc_type']}  chunk_index={c['chunk_index']}  tokens={token_counts[i]}")
        print(c["text"][:500])
