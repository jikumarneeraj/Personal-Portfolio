import os
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple

DATA_DIR = Path(__file__).resolve().parent / "data"

class KnowledgeChunk:
    def __init__(self, doc_name: str, section_title: str, content: str):
        self.doc_name = doc_name
        self.section_title = section_title
        self.content = content
        self.full_text = f"## {section_title}\n{content}"
        self.tokens = self._tokenize(self.full_text)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 2]

class PortfolioRAG:
    def __init__(self):
        self.chunks: List[KnowledgeChunk] = []
        self.idf: Dict[str, float] = {}
        self.doc_freq: Dict[str, int] = {}
        self._load_knowledge()

    def _load_knowledge(self):
        """Loads all markdown files from the data directory and splits them into logical chunks."""
        self.chunks.clear()
        if not DATA_DIR.exists():
            return

        for file_path in DATA_DIR.glob("*.md"):
            doc_name = file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                
                # Split by level 2 headings (## )
                sections = re.split(r"\n(?=##\s+)", text)
                for sec in sections:
                    sec = sec.strip()
                    if not sec:
                        continue
                    
                    lines = sec.split("\n", 1)
                    header_line = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ""
                    
                    title = header_line.lstrip("#").strip()
                    chunk = KnowledgeChunk(doc_name, title, body)
                    self.chunks.append(chunk)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        # Compute IDF
        total_docs = len(self.chunks)
        if total_docs == 0:
            return

        for chunk in self.chunks:
            unique_tokens = set(chunk.tokens)
            for token in unique_tokens:
                self.doc_freq[token] = self.doc_freq.get(token, 0) + 1

        for token, freq in self.doc_freq.items():
            self.idf[token] = math.log((total_docs + 1) / (freq + 0.5)) + 1.0

    def retrieve(self, query: str, top_k: int = 4) -> List[Tuple[KnowledgeChunk, float]]:
        """
        Retrieves top_k most relevant knowledge chunks for a given query using BM25-style scoring.
        """
        if not self.chunks:
            return []

        query_tokens = KnowledgeChunk._tokenize(query)
        if not query_tokens:
            # If empty or generic query, return top general chunks (about + skills)
            default_chunks = [c for c in self.chunks if c.doc_name in ["about", "skills", "projects"]]
            return [(c, 1.0) for c in default_chunks[:top_k]]

        scores: List[Tuple[KnowledgeChunk, float]] = []
        k1 = 1.5
        b = 0.75
        avg_doc_len = sum(len(c.tokens) for c in self.chunks) / max(len(self.chunks), 1)

        for chunk in self.chunks:
            score = 0.0
            doc_len = len(chunk.tokens)
            chunk_token_counts: Dict[str, int] = {}
            for t in chunk.tokens:
                chunk_token_counts[t] = chunk_token_counts.get(t, 0) + 1

            for q_tok in query_tokens:
                if q_tok in chunk_token_counts:
                    tf = chunk_token_counts[q_tok]
                    idf_val = self.idf.get(q_tok, 1.0)
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (doc_len / avg_doc_len))
                    score += idf_val * (numerator / denominator)

            # Bonus for exact title matches
            title_lower = chunk.section_title.lower()
            if any(q_tok in title_lower for q_tok in query_tokens):
                score += 2.5

            # Intent boost for relevant document category
            q_str = " ".join(query_tokens)
            if ("skill" in q_str or "technolog" in q_str or "tool" in q_str or "stack" in q_str) and chunk.doc_name == "skills":
                score += 15.0
            elif ("project" in q_str or "built" in q_str or "work" in q_str or "repo" in q_str) and chunk.doc_name == "projects":
                score += 15.0
            elif ("education" in q_str or "degree" in q_str or "college" in q_str or "iit" in q_str or "rec" in q_str) and chunk.doc_name in ["education", "about"]:
                score += 10.0
            elif ("intern" in q_str or "experience" in q_str or "role" in q_str or "leader" in q_str or "lenovo" in q_str) and chunk.doc_name == "experience":
                score += 10.0
            elif ("certificate" in q_str or "gate" in q_str or "award" in q_str or "hackerrank" in q_str) and chunk.doc_name in ["certifications", "achievements"]:
                score += 10.0

            # Discard empty body chunks
            if not chunk.content.strip():
                score = -1.0

            scores.append((chunk, score))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def get_context_for_query(self, query: str, top_k: int = 8) -> str:
        """Returns formatted string of retrieved chunks to be used in LLM prompt."""
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return ""

        context_parts = []
        for chunk, score in results:
            context_parts.append(
                f"### [{chunk.doc_name.upper()}] {chunk.section_title}\n{chunk.content}"
            )
        return "\n\n---\n\n".join(context_parts)

    def get_all_portfolio_summary(self) -> str:
        """Returns a concise high-level overview from all documents."""
        parts = []
        for chunk in self.chunks:
            if chunk.doc_name in ["about", "skills", "projects"]:
                parts.append(f"### {chunk.section_title}\n{chunk.content}")
        return "\n\n".join(parts[:5])

portfolio_rag = PortfolioRAG()
