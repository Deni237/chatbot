import os
os.environ['USE_TF'] = 'NO'
os.environ['USE_TORCH'] = 'YES'
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from processing.chunking import load_documents, chunk_documents

def get_embedding_model():
    """
    Initialise le modèle d'embeddings local.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings

# if __name__ == "__main__":
#     embeddings = get_embedding_model()

#     test_vector = embeddings.embed_query("test embedding")
#     print(f"Taille du vecteur : {len(test_vector)}")

def get_vector_store(chunks, embeddings, persist_directory="vectorstore"):
    """
    Crée ou charge une base vectorielle Chroma persistante.
    """
    os.makedirs(persist_directory, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    return vector_store


if __name__ == "__main__":
    # Charger et découper les documents (limités pour test)
    docs = load_documents()
    chunks = chunk_documents(docs)

    embeddings = get_embedding_model()
    vector_store = get_vector_store(chunks, embeddings)

    print("Base vectorielle initialisée et persistée.")
#test de recherche vectorielle
if __name__ == "__main__":
    from processing.chunking import load_documents, chunk_documents

    docs = load_documents()
    chunks = chunk_documents(docs)

    embeddings = get_embedding_model()
    vector_store = get_vector_store(chunks, embeddings)

    query = "admission aux programmes d'études"
    results = vector_store.similarity_search(query, k=3)

    print(f"Requête : {query}\n")
    for i, doc in enumerate(results, 1):
        print(f"Résultat {i}")
        print("Source :", doc.metadata.get("source"))
        print(doc.page_content[:300])
        print("-" * 50)
