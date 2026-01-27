import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from scraper.scraper import (
    BASE_URL,
    collect_links,
    extract_html_content,
    extract_pdf_content
)
def load_documents():
    """
    Charge et structure les documents issus du web scraping.
    """
    documents = []

    html_links, pdf_links = collect_links(BASE_URL)

    # Traitement des pages HTML
    for url in html_links[:20]:
        text = extract_html_content(url)
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": url,
                        "type": "html"
                    }
                )
            )

    # Traitement des PDF
    for url in pdf_links:
        text = extract_pdf_content(url)
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": url,
                        "type": "pdf"
                    }
                )
            )

    return documents

# if __name__ == "__main__":
#     docs = load_documents()

#     print(f"Nombre total de documents chargés : {len(docs)}")

#     if docs:
#         print("Exemple de document :")
#         print(docs[0].metadata)
#         print(docs[0].page_content[:500])
def chunk_documents(documents):
    """
    Découpe les documents en chunks avec chevauchement.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80
    )

    chunks = text_splitter.split_documents(documents)
    return chunks
if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)

    print(f"Nombre de documents initiaux : {len(docs)}")
    print(f"Nombre total de chunks : {len(chunks)}")

    if chunks:
        print("Exemple de chunk :")
        print(chunks[0].metadata)
        print(chunks[0].page_content[:500])
# non_empty_chunks = [c for c in chunks if c.page_content.strip()]
# avg_size = sum(len(c.page_content) for c in non_empty_chunks) / len(non_empty_chunks)

# print(f"Chunks non vides : {len(non_empty_chunks)}")
# print(f"Taille moyenne des chunks : {int(avg_size)} caractères")
