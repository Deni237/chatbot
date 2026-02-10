"""
Chatbot UQAC — Interface Web Streamlit
Interface utilisateur moderne pour le pipeline RAG
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).resolve().parent))

from embeddings.vector_store import get_embedding_model, get_vector_store
from langchain_community.llms import Ollama as OllamaLLM
from memoire.memory import create_memory
from processing.chunking import load_documents, chunk_documents

# ══════════════════════════════════════════════════════════════════════════════
# Configuration de la page
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Chatbot UQAC",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# Styles CSS personnalisés
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    :root {
        --uqac-blue: #003366;
        --uqac-light-blue: #0066CC;
        --uqac-gold: #DAA520;
    }
    
    .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid #0066CC;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0066CC 0%, #003366 50%, #DAA520 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-subtitle {
        font-size: 1rem;
        color: #666;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Initialisation des composants (avec cache)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def initialize_rag_components():
    """Initialise les composants RAG une seule fois"""
    docs = load_documents()
    chunks = chunk_documents(docs)
    embeddings = get_embedding_model()
    vector_store = get_vector_store(chunks, embeddings, persist_directory="vectorstore")
    model = OllamaLLM(model="tinyllama")
    return vector_store, model

# ══════════════════════════════════════════════════════════════════════════════
# Fonctions utilitaires
# ══════════════════════════════════════════════════════════════════════════════

def rag_query(query: str, vector_store, model, memory, top_k: int = 5):
    """Exécute une requête RAG et retourne la réponse avec les sources"""
    
    # Recherche des documents pertinents
    retrieved_docs = vector_store.similarity_search(query, k=top_k)
    
    # Construction du contexte
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Historique de conversation
    history = memory.get_messages()
    history_text = "\n".join([f"{m.type.upper()}: {m.content}" for m in history])
    
    # Template de prompt
    template = f"""
    Conversation précédente :
    {history_text}

    Contexte :
    Réponds UNIQUEMENT en français.

    {context}

    Question :
    {query}
    """
    
    # Génération de la réponse
    response = model.invoke(template)
    
    # Sauvegarde dans la mémoire
    memory.add_turn(query, response)
    
    # Extraction des sources uniques
    sources = list(set([doc.metadata.get("source", "Source inconnue") for doc in retrieved_docs]))
    
    return response, sources

# ══════════════════════════════════════════════════════════════════════════════
# Interface principale
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Initialisation de la session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "memory" not in st.session_state:
        st.session_state.memory = create_memory()
    
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    # ══════════════════════════════════════════════════════════════════════════
    # Sidebar
    # ══════════════════════════════════════════════════════════════════════════
    
    with st.sidebar:
        st.markdown("## 🎓 UQAC")
        st.markdown("---")
        
        st.markdown("### ⚙️ Paramètres")
        
        top_k = st.slider(
            "Nombre de sources",
            min_value=1,
            max_value=10,
            value=5,
            help="Nombre de segments de texte à utiliser pour générer la réponse"
        )
        
        st.markdown("---")
        
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.messages = []
            st.session_state.memory = create_memory()
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📊 Statistiques")
        st.metric("Messages", len(st.session_state.messages))
        
        st.markdown("---")
        
        st.markdown("""
        **À propos**  
        Ce chatbot utilise un pipeline RAG pour répondre aux questions 
        basées sur le Manuel de gestion de l'UQAC.
        """)

    # ══════════════════════════════════════════════════════════════════════════
    # Header principal
    # ══════════════════════════════════════════════════════════════════════════
    
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🎓 Chatbot UQAC</div>
        <div class="main-subtitle">Assistant intelligent basé sur le Manuel de gestion</div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # Chargement des composants RAG
    # ══════════════════════════════════════════════════════════════════════════
    
    if not st.session_state.initialized:
        with st.spinner("🔄 Chargement du système RAG..."):
            try:
                vector_store, model = initialize_rag_components()
                st.session_state.vector_store = vector_store
                st.session_state.model = model
                st.session_state.initialized = True
            except Exception as e:
                st.error(f"❌ Erreur lors de l'initialisation : {str(e)}")
                st.stop()

    # ══════════════════════════════════════════════════════════════════════════
    # Zone de chat
    # ══════════════════════════════════════════════════════════════════════════
    
    # Afficher le message de bienvenue si pas de messages
    if not st.session_state.messages:
        st.info("""
        💬 **Bienvenue !**  
        Je suis votre assistant pour le Manuel de gestion de l'UQAC.  
        Posez-moi vos questions sur les politiques, procédures et règlements de l'université.
        
        **Suggestions :**  
        📋 Politiques académiques • 📅 Calendrier universitaire • 💼 Ressources humaines
        """)
    
    # Afficher l'historique des messages avec les composants natifs Streamlit
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
                
                # Afficher les sources de manière propre
                if message.get("sources"):
                    with st.expander("📚 Sources consultées", expanded=False):
                        for source in message["sources"]:
                            if source and source != "Source inconnue":
                                st.markdown(f"🔗 [{source}]({source})")
                            elif source:
                                st.markdown(f"📄 {source}")

    # ══════════════════════════════════════════════════════════════════════════
    # Zone de saisie
    # ══════════════════════════════════════════════════════════════════════════
    
    # Input utilisateur
    user_input = st.chat_input("Posez votre question sur le Manuel de gestion...")
    
    if user_input:
        # Ajouter et afficher le message utilisateur
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Générer la réponse
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Recherche en cours..."):
                try:
                    response, sources = rag_query(
                        user_input,
                        st.session_state.vector_store,
                        st.session_state.model,
                        st.session_state.memory,
                        top_k=top_k
                    )
                    
                    # Afficher la réponse
                    st.markdown(response)
                    
                    # Afficher les sources
                    if sources:
                        with st.expander("📚 Sources consultées", expanded=False):
                            for source in sources:
                                if source and source != "Source inconnue":
                                    st.markdown(f"🔗 [{source}]({source})")
                                elif source:
                                    st.markdown(f"📄 {source}")
                    
                    # Ajouter la réponse à l'historique
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération de la réponse : {str(e)}")


if __name__ == "__main__":
    main()