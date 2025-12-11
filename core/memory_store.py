import os
import logging
import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional

# --- Configuration ---
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# We use a separate logger for memory operations
logger = logging.getLogger(__name__)

class MemoryStore:
    """
    The Hippocampus (Long-Term Memory).
    Manages the Vector Database for RAG (Retrieval Augmented Generation).
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.db_path = project_root / "data" / "memory_db"
        
        # RAG Configuration
        self.use_rag = os.getenv("USE_RAG", "false").lower() == "true"
        self.embedding_model = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
        self.api_key = os.getenv("LLM_API_KEY")

        # Initialize ChromaDB Client
        if self.use_rag:
            try:
                self.client = chromadb.PersistentClient(path=str(self.db_path))
                # Create or get the collection for this project's narrative
                self.collection = self.client.get_or_create_collection(
                    name="narrative_memory",
                    metadata={"hnsw:space": "cosine"} # Cosine similarity for text search
                )
                self.openai_client = OpenAI(api_key=self.api_key)
                logger.info(f"MemoryStore initialized at {self.db_path}")
            except Exception as e:
                logger.error(f"Failed to initialize MemoryStore: {e}")
                self.use_rag = False

    def _get_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text using OpenAI."""
        if not self.use_rag:
            return []
            
        try:
            # Clean text
            text = text.replace("\n", " ")
            response = self.openai_client.embeddings.create(
                input=[text],
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    def ingest_manuscript(self, file_path: Path, content: str):
        """
        Chunks and vectorizes a manuscript file.
        Should be called by the Scanner when a file is modified.
        """
        if not self.use_rag:
            return

        try:
            file_id = file_path.stem # e.g., "ch01_Start"
            
            # 1. Clear existing memory for this file (to avoid duplicates on update)
            # Note: ChromaDB's delete by 'where' clause
            self.collection.delete(where={"source": file_id})

            # 2. Chunking Strategy (Simple paragraph-based for now)
            # In a real app, we'd use a token-aware splitter (RecursiveCharacterTextSplitter)
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
            
            if not paragraphs:
                return

            # 3. Batch Process
            ids = []
            documents = []
            metadatas = []
            embeddings = []

            for idx, para in enumerate(paragraphs):
                chunk_id = f"{file_id}_{idx}"
                embedding = self._get_embedding(para)
                
                if embedding:
                    ids.append(chunk_id)
                    documents.append(para)
                    embeddings.append(embedding)
                    metadatas.append({
                        "source": file_id,
                        "type": "narrative",
                        "chunk_index": idx
                    })

            # 4. Upsert to DB
            if ids:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                logger.info(f"Ingested {len(ids)} chunks from {file_id}")

        except Exception as e:
            logger.error(f"Failed to ingest manuscript {file_path}: {e}")

    def query(self, query_text: str, n_results: int = 5) -> str:
        """
        Retrieves relevant context from the vector database.
        Returns a formatted string of the top N matches.
        """
        if not self.use_rag:
            return "Memory System Offline."

        try:
            # 1. Vectorize Query
            query_embedding = self._get_embedding(query_text)
            if not query_embedding:
                return ""

            # 2. Search DB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # 3. Format Results
            # Chroma returns lists of lists (batch format)
            retrieved_docs = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            formatted_context = []
            for doc, meta in zip(retrieved_docs, metadatas):
                source = meta.get('source', 'unknown')
                formatted_context.append(f"[{source}]: {doc}")

            return "\n---\n".join(formatted_context)

        except Exception as e:
            logger.error(f"Memory Query failed: {e}")
            return ""

    def clear_memory(self):
        """Wipes the database. Use with caution."""
        if self.use_rag:
            try:
                self.client.delete_collection("narrative_memory")
                logger.warning("MemoryStore wiped.")
            except Exception as e:
                logger.error(f"Failed to clear memory: {e}")