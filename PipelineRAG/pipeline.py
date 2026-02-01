import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from embeddings.vector_store import get_embedding_model, get_vector_store
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


from processing.chunking import load_documents, chunk_documents


# Charger et préparer les documents + vector store UNE FOIS
print("Chargement des documents et création du vector store…")
docs = load_documents()
chunks = chunk_documents(docs)
embeddings = get_embedding_model()
vector_store = get_vector_store(chunks, embeddings, persist_directory="vectorstore")

# Initialiser le LLM
model = OllamaLLM(model="tinyllama")  # ou ton modèle local

def rag_pipeline(query, top_k=5):
   
    # Recherche top-k
    retrieved_docs = vector_store.similarity_search(query, k=top_k)

    # Construire le contexte pour le prompt
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    template = f"""
    Réponds à la question suivante en français uniquement.

    Context :
    {context}

    Question :
    {query}

    """

    #prompt = ChatPromptTemplate.from_template(template)
    #chain = prompt|model
    # Générer la réponse
    response = model.invoke([template])

    # Retourner la réponse et les sources
    sources = [doc.metadata.get("source") for doc in retrieved_docs]
    return response, sources

# utilisation
if __name__ == "__main__":
    
    print("=== Pipeline RAG ===")
    print("Tapez 'exit' pour quitter.\n")

    while True:
        query = input("Entrez votre question : ")
        if query.lower() in ["exit"]:
            break

        response, sources = rag_pipeline(query)
        print("\nRéponse :\n", response)
        print("\nSources utilisées :")
        for s in sources:
            print("-", s)
        print("\n" + "="*50 + "\n")