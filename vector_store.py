"""
Embedding + vector store for The Unofficial Guide (NYU off-campus housing).

Embeds chunks from chunker.py with all-MiniLM-L6-v2 (sentence-transformers,
runs locally — no API key) and stores them in a persistent ChromaDB collection
with source metadata (filename, doc_type, chunk_index) for later attribution.

Usage:
    python3 vector_store.py            # builds the store (if empty) and runs sample queries
    from vector_store import retrieve   # for use in the generation step
"""

import chromadb
from sentence_transformers import SentenceTransformer

from chunker import chunk_all_documents

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "unofficial_guide_housing"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

_model = None
_client = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def build_store(force: bool = False) -> int:
    """Embed all chunks and load them into ChromaDB. Returns the chunk count.

    Idempotent: if the collection is already populated, this is a no-op unless
    force=True (e.g., after changing the chunking strategy).
    """
    collection = _get_collection()

    if collection.count() > 0:
        if not force:
            print(f"Collection already has {collection.count()} chunks — skipping build "
                  f"(pass force=True to rebuild).")
            return collection.count()
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)

    chunks = chunk_all_documents()
    model = _get_model()

    texts = [c["text"] for c in chunks]
    ids = [f"{c['source']}::{c['chunk_index']}" for c in chunks]
    metadatas = [
        {"source": c["source"], "doc_type": c["doc_type"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    print(f"Embedding {len(texts)} chunks with {EMBEDDING_MODEL_NAME}...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64).tolist()

    # ChromaDB has an internal batch-size limit — add in chunks of 1000
    BATCH = 1000
    for i in range(0, len(ids), BATCH):
        collection.add(
            ids=ids[i:i + BATCH],
            documents=texts[i:i + BATCH],
            embeddings=embeddings[i:i + BATCH],
            metadatas=metadatas[i:i + BATCH],
        )

    print(f"Stored {collection.count()} chunks in ChromaDB at ./{CHROMA_PATH}")
    return collection.count()


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Return the top-k most relevant chunks for a query.

    Each result: {"text": ..., "source": ..., "doc_type": ..., "chunk_index": ..., "distance": ...}
    Lower distance = more semantically similar (cosine distance).
    """
    collection = _get_collection()
    model = _get_model()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    hits = []
    for text, meta, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        hits.append({
            "text": text,
            "source": meta["source"],
            "doc_type": meta["doc_type"],
            "chunk_index": meta["chunk_index"],
            "distance": distance,
        })
    return hits


SAMPLE_QUERIES = [
    "What do commenters say about the trade-offs of living in Astoria versus Williamsburg?",
    "What does the NYU Lease Guarantor article say a student needs without a US-based co-signer?",
    "What specific safety concerns do commenters raise about Washington Heights near 161st Street?",
]


if __name__ == "__main__":
    build_store()

    print("\n--- Test retrieval on sample evaluation queries ---")
    for query in SAMPLE_QUERIES:
        print(f"\nQuery: {query}")
        for rank, hit in enumerate(retrieve(query), start=1):
            preview = hit["text"][:200].replace("\n", " ")
            print(f"  [{rank}] distance={hit['distance']:.3f}  source={hit['source']}  doc_type={hit['doc_type']}")
            print(f"       {preview}...")
