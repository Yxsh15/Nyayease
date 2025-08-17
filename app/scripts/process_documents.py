import asyncio
import os
import sys

# Add the parent directory to the Python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.vector_service import VectorService

async def main():
    """
    This script processes all the documents in the legal_documents directory and stores them in the vector database.
    """
    # Create an instance of the VectorService
    vector_service = VectorService()

    # Get the path to the legal_documents directory
    legal_documents_dir = os.path.join(os.path.dirname(__file__), '..', 'legal_documents')

    # Get the list of files in the directory
    document_paths = [os.path.join(legal_documents_dir, f) for f in os.listdir(legal_documents_dir) if os.path.isfile(os.path.join(legal_documents_dir, f))]

    # Process and store the documents
    if document_paths:
        print(f"Processing {len(document_paths)} documents...")
        await vector_service.process_and_store_documents(document_paths)
        print("Documents processed and stored successfully.")
    else:
        print("No documents found in the legal_documents directory.")

if __name__ == "__main__":
    # To avoid RuntimeError: Event loop is closed
    # https://docs.python.org/3/library/asyncio-policy.html#asyncio.WindowsSelectorEventLoopPolicy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())