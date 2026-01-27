# chatbot
Chatbot UQAC — Pipeline RAG (Travail réalisé)
Description générale

Ce projet vise à implémenter un chatbot, capable de répondre à des questions à partir du Manuel de gestion de l’UQAC.

Structure générale du projet à ce jour(27/01/2026)
chatbot/
│
├── scraper/
│   └── scraper.py              # Phase 1 — Web scraping
│
├── processing/
│   ├── __init__.py
│   └── chunking.py             # Phase 2 — Structuration & chunking
│
├── embeddings/
│   └── vector_store.py         # Phase 3 — Embeddings & base vectorielle
│
├── vectorstore/                # Base vectorielle persistante (ChromaDB)
│   └── (fichiers générés automatiquement)
│
└── README.md

Phase 1 — Web scraping et extraction des contenus
Objectif

Collecter automatiquement les contenus pertinents du Manuel de gestion de l’UQAC (pages HTML et documents PDF).

Fichiers concernés
scraper/
└── scraper.py

Réalisations

Exploration automatique du site https://www.uqac.ca/mgestion/

Filtrage des liens internes pertinents

Séparation des ressources :

pages HTML

documents PDF

Extraction ciblée du contenu HTML depuis :

div.entry-header

div.entry-content

Téléchargement temporaire des PDF et extraction du texte

Nettoyage léger des textes (espaces multiples, lignes vides)

Gestion robuste des erreurs :

liens obsolètes

erreurs HTTP 404

PDF inaccessibles

Résultat

Un corpus textuel propre et traçable (URL source conservée), prêt pour le traitement RAG.

Phase 2 — Structuration et découpage des textes (Chunking)
Objectif

Préparer les textes extraits pour l’indexation vectorielle.

Fichiers concernés
processing/
├── __init__.py
└── chunking.py

Réalisations

Transformation des contenus extraits en objets Document (LangChain)

Conservation des métadonnées :

URL source

type de contenu (HTML / PDF)

Découpage des textes avec RecursiveCharacterTextSplitter

taille des chunks ≈ 500 caractères

chevauchement ≈ 80 caractères

Validation du découpage :

aucun chunk vide

taille moyenne cohérente (~486 caractères)

Résultat

Environ 500 segments textuels cohérents, prêts à être vectorisés.

Phase 3 — Embeddings et base vectorielle (persistance locale)
Objectif

Indexer les chunks dans une base vectorielle locale persistante afin de permettre la recherche sémantique.

Fichiers et dossiers concernés
embeddings/
└── vector_store.py

vectorstore/
└── (index et fichiers internes ChromaDB)

Réalisations

Utilisation d’un modèle d’embeddings local :

sentence-transformers/all-MiniLM-L6-v2

Génération des embeddings pour chaque chunk

Stockage des vecteurs, textes et métadonnées dans une base ChromaDB

Persistance locale sur disque (vectorstore/)

Test de recherche vectorielle (sanity check) :

requêtes sémantiques

récupération des segments pertinents

affichage des URLs sources associées

Résultat

Une base vectorielle locale fonctionnelle, persistante et interrogeable.
