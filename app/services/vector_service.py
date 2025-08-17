import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from typing import List, Dict, Any
from app.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        self.collection_name = "legal_documents"
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Indian Legal Documents Collection"}
            )
    
    async def process_and_store_documents(self, document_paths: List[str]) -> bool:
        """Process legal documents and store in vector database"""
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
            )
            
            all_chunks = []
            metadatas = []
            ids = []
            
            for doc_path in document_paths:
                # Load document
                loader = PyMuPDFLoader(doc_path)
                documents = loader.load()
                
                # Split into chunks
                chunks = text_splitter.split_documents(documents)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_path.split('/')[-1]}_{i}_{uuid.uuid4().hex[:8]}"
                    ids.append(chunk_id)
                    all_chunks.append(chunk.page_content)
                    metadatas.append({
                        "source": doc_path,
                        "chunk_index": i,
                        "document_type": self._get_document_type(doc_path),
                        "page": chunk.metadata.get("page", 0)
                    })
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(all_chunks)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=all_chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully processed and stored {len(all_chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            return False
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search on vector database"""
        logger.info(f"Performing similarity search for query: {query}")
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            for i in range(len(results["documents"][0])):
                search_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "relevance_score": 1 - results["distances"][0][i]
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def _get_document_type(self, file_path: str) -> str:
        """Determine document type from file path"""
        file_name = file_path.lower()
        if "constitution" in file_name:
            return "constitution"
        elif "ipc" in file_name:
            return "ipc"
        elif "crpc" in file_name:
            return "crpc"
        else:
            return "act"
