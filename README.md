# chatbot

Chatbot UQAC — Pipeline RAG (Travail réalisé)
Description générale

Ce projet vise à implémenter un chatbot, capable de répondre à des questions à partir du Manuel de gestion de l’UQAC.

Structure générale du projet à ce jour(31/01/2026)

chatbot/
│
├── scraper/
│ └── scraper.py # Phase 1 — Web scraping
│
├── processing/
│ ├── init.py
│ └── chunking.py # Phase 2 — Structuration & chunking
│
├── embeddings/
│ └── vector_store.py # Phase 3 — Embeddings & base vectorielle
│
├── vectorstore/ # Base vectorielle persistante (ChromaDB)
│ └── (fichiers générés automatiquement)
│
├── pipelineRAG/
│ └── pipeline.py # Phase 4 — Pipeline RAG
│
└── README.md

## Phase 1 — Web scraping et extraction des contenus

**Objectif**  
Collecter automatiquement les contenus pertinents du Manuel de gestion de l’UQAC (pages HTML et documents PDF).

**Fichiers concernés**  
`scraper/scraper.py`

**Réalisations**

- Exploration automatique du site [UQAC — Manuel de gestion](https://www.uqac.ca/mgestion/)
- Filtrage des liens internes pertinents
- Séparation des ressources :
  - pages HTML
  - documents PDF
- Extraction ciblée du contenu HTML depuis :
  - `div.entry-header`
  - `div.entry-content`
- Téléchargement temporaire des PDF et extraction du texte
- Nettoyage léger des textes (espaces multiples, lignes vides)
- Gestion robuste des erreurs :
  - liens obsolètes
  - erreurs HTTP 404
  - PDF inaccessibles

**Résultat**  
Un corpus textuel propre et traçable (URL source conservée), prêt pour le traitement RAG.

---

## Phase 2 — Structuration et découpage des textes (Chunking)

**Objectif**  
Préparer les textes extraits pour l’indexation vectorielle.

**Fichiers concernés**  
`processing/chunking.py`

**Réalisations**

- Transformation des contenus extraits en objets `Document` (LangChain)
- Conservation des métadonnées :
  - URL source
  - type de contenu (HTML / PDF)
- Découpage des textes avec `RecursiveCharacterTextSplitter` :
  - taille des chunks ≈ 500 caractères
  - chevauchement ≈ 80 caractères
- Validation du découpage :
  - aucun chunk vide
  - taille moyenne cohérente (~486 caractères)

**Résultat**  
Environ 500 segments textuels cohérents, prêts à être vectorisés.

---

## Phase 3 — Embeddings et base vectorielle (persistance locale)

**Objectif**  
Indexer les chunks dans une base vectorielle locale persistante afin de permettre la recherche sémantique.

**Fichiers et dossiers concernés**

- `embeddings/vector_store.py`
- `vectorstore/` (index et fichiers internes ChromaDB)

**Réalisations**

- Utilisation d’un modèle d’embeddings local : `sentence-transformers/all-MiniLM-L6-v2`
- Génération des embeddings pour chaque chunk
- Stockage des vecteurs, textes et métadonnées dans une base ChromaDB
- Persistance locale sur disque (`vectorstore/`)
- Test de recherche vectorielle (sanity check) :
  - requêtes sémantiques
  - récupération des segments pertinents
  - affichage des URLs sources associées

**Résultat**  
Une base vectorielle locale fonctionnelle, persistante et interrogeable.

---

## Phase 4 — Pipeline RAG (Retrieval-Augmented Generation)

**Objectif**  
Implémenter une chaîne RAG complète basée sur LangChain pour générer des réponses contextualisées à partir du Manuel de gestion.

**Fichiers concernés**  
`pipelineRAG/pipeline.py`

**Réalisations**

- Intégration de la base vectorielle Chroma pour la recherche sémantique des chunks
- Création d’un prompt dynamique combinant :
  - Contexte extrait via la recherche vectorielle (top-k chunks)
  - Question de l’utilisateur
- Utilisation d’un modèle de langage local (ex : `tinyllama` via Ollama) pour générer les réponses
- Gestion des sources pour chaque réponse
- Boucle interactive permettant de poser des questions et recevoir des réponses contextualisées avec les URLs des sources

**Résultat**  
Un chatbot capable de répondre de manière contextuelle aux questions sur le Manuel de gestion de l’UQAC, avec traçabilité des sources utilisées.

## Instructions pour exécuter le projet Chatbot UQAC — Pipeline RAG

**1. Cloner le dépôt**

Ouvrir un terminal (Git Bash ou CMD) et exécuter :

- git clone https://github.com/Deni237/chatbot
- cd chatbot

**2. Créer et activer un environnement virtuel Python**

Ceci permet de garder les dépendances isolées.

- python -m venv env
- .\env\Scripts\activate

**3. Installer les dépendances**

Installer toutes les librairies nécessaires via le fichier requirements.txt :

- pip install --upgrade pip
- pip install -r requirements.txt

**4. Installer Ollama et télécharger un modèle léger**

a) Installer Ollama

Télécharger le binaire Ollama pour Windows, macOS ou Linux depuis : https://ollama.com/download

Suivre les instructions d’installation (il doit être accessible via ollama dans le terminal)

b) Vérifier l’installation

- ollama --version
  Si la commande retourne une version, Ollama est correctement installé.

c) Télécharger un modèle léger (tinyllama)

- ollama pull tinyllama

**5. Lancer le pipeline RAG**

Depuis le terminal et avec l’environnement activé :

- python pipeline.py

Ensuite, entrez votre question et attendez la reponse du chatbot
