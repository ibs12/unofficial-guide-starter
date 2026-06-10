"""
Document ingestion for The Unofficial Guide (NYU off-campus housing).

Loads two kinds of source documents from documents/:
  - documents/reddit/*.txt        Reddit threads (already parsed into
                                  POST TITLE / POST BODY / COMMENT blocks
                                  by jsontotext.py)
  - documents/nyu_official/*.pdf  NYU Off-Campus Housing Search articles,
                                  saved as browser "print to PDF" exports

Produces a list of cleaned documents, each a dict:
    {"source": <filename>, "doc_type": "reddit" | "nyu_official", "text": <cleaned text>}

ready to be handed to the chunker.
"""

import os
import re

import pdfplumber

REDDIT_DIR = os.path.join("documents", "reddit")
NYU_PDF_DIR = os.path.join("documents", "nyu_official")

# Matches the browser "print to PDF" header NYU pages carry on every page,
# e.g. "6/7/26, 9:29 AM Resources | New York University | Off-Campus Housing Search"
PRINT_HEADER_RE = re.compile(
    r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M\s+Resources \| New York University \| Off-Campus Housing Search$"
)

# Matches the footer NYU pages carry on every page, e.g.
# "https://offcampushousing.nyu.edu/resources/article/3408-avoiding-rental-scams 1/4"
PRINT_FOOTER_RE = re.compile(
    r"^https://offcampushousing\.nyu\.edu/\S+ \d+/\d+$"
)

# Trailing site boilerplate that shows up at the end of every NYU article
NYU_BOILERPLATE_RE = re.compile(
    r"^(Was this article helpful\??|Related Articles|Still need help\?.*|Contact Us.*)$",
    re.IGNORECASE,
)

# Bare URLs and markdown-style links left over in Reddit comments
URL_RE = re.compile(r"\(?https?://\S+\)?")


def clean_reddit_text(raw: str) -> str:
    """Light cleanup for already-structured Reddit thread text.

    The .txt files are pre-formatted as POST TITLE / POST BODY / COMMENT
    blocks by jsontotext.py, so the main job here is stripping raw URLs
    (which carry no semantic value for retrieval and bloat the embeddings)
    and collapsing extra whitespace left behind.
    """
    text = URL_RE.sub("", raw)
    # collapse runs of blank lines down to a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # collapse runs of spaces/tabs created by removing inline URLs
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def clean_nyu_text(raw: str) -> str:
    """Strip browser print-to-PDF headers/footers and site boilerplate."""
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if PRINT_HEADER_RE.match(stripped):
            continue
        if PRINT_FOOTER_RE.match(stripped):
            continue
        if NYU_BOILERPLATE_RE.match(stripped):
            continue
        lines.append(stripped)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_reddit_documents() -> list[dict]:
    documents = []
    for filename in sorted(os.listdir(REDDIT_DIR)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(REDDIT_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = clean_reddit_text(raw)
        if cleaned:
            documents.append({"source": filename, "doc_type": "reddit", "text": cleaned})
    return documents


def load_nyu_documents() -> list[dict]:
    documents = []
    for filename in sorted(os.listdir(NYU_PDF_DIR)):
        if not filename.endswith(".pdf"):
            continue
        path = os.path.join(NYU_PDF_DIR, filename)
        with pdfplumber.open(path) as pdf:
            raw = "\n\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        cleaned = clean_nyu_text(raw)
        if cleaned:
            documents.append({"source": filename, "doc_type": "nyu_official", "text": cleaned})
    return documents


def load_documents() -> list[dict]:
    """Load and clean every source document. Returns a flat list ready for chunking."""
    return load_reddit_documents() + load_nyu_documents()


EXTRACTED_TEXT_DIR = os.path.join("documents", "nyu_official_extracted")


def save_extracted_pdf_text(documents: list[dict] | None = None) -> None:
    """Write the cleaned text pulled from each NYU PDF to a .txt file.

    pdfplumber only extracts text in memory — this persists the cleaned result
    as a stable, inspectable intermediate artifact (one .txt per source PDF),
    so you can read exactly what the chunker will see without re-running
    extraction every time.
    """
    os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
    documents = documents or load_nyu_documents()
    for doc in documents:
        if doc["doc_type"] != "nyu_official":
            continue
        out_name = os.path.splitext(doc["source"])[0] + ".txt"
        out_path = os.path.join(EXTRACTED_TEXT_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(doc["text"])
    print(f"Wrote {sum(1 for d in documents if d['doc_type'] == 'nyu_official')} "
          f"extracted/cleaned PDF text files to {EXTRACTED_TEXT_DIR}/")


if __name__ == "__main__":
    docs = load_documents()
    save_extracted_pdf_text(docs)
    reddit_count = sum(1 for d in docs if d["doc_type"] == "reddit")
    nyu_count = sum(1 for d in docs if d["doc_type"] == "nyu_official")

    print(f"Loaded {len(docs)} documents ({reddit_count} reddit threads, {nyu_count} NYU official articles)\n")

    # Print one of each type so you can eyeball that cleaning worked —
    # no leftover HTML, print-header lines, or raw URLs.
    for doc_type in ("reddit", "nyu_official"):
        sample = next(d for d in docs if d["doc_type"] == doc_type)
        print(f"=== Sample [{doc_type}] — {sample['source']} ===")
        print(sample["text"][:1000])
        print("...\n")
