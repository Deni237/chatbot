# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tempfile
import os
from pypdf import PdfReader
import re


from typing import List, Set

# URL racine du manuel de gestion
BASE_URL = "https://www.uqac.ca/mgestion/"

# évite les doublons
visited_urls: Set[str] = set()


urls_to_visit: List[str] = [BASE_URL]

#RECUPERER LES DIFFERENTS LIENS
def collect_links(url: str):
    """
    Télécharge une page HTML et extrait les liens pertinents.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de l'accès à {url} : {e}")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")

    html_links = []
    pdf_links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Construction de l'URL absolue
        full_url = urljoin(url, href)

        # Filtrage : uniquement le domaine du manuel
        if not full_url.startswith(BASE_URL):
            continue

        # Nettoyage des ancres (#)
        full_url = full_url.split("#")[0]

        if full_url.endswith(".pdf"):
            pdf_links.append(full_url)
        else:
            html_links.append(full_url)

    return list(set(html_links)), list(set(pdf_links))

# if __name__ == "__main__":
#     print("Scraper initialisé")
#     print(f"URL de départ : {BASE_URL}")

#     html_links, pdf_links = collect_links(BASE_URL)

#     print(f"Liens HTML trouvés : {len(html_links)}")
#     print(f"Liens PDF trouvés : {len(pdf_links)}")

#     print("Exemples HTML :", html_links[:3])
#     print("Exemples PDF :", pdf_links[:3])

#EXTRACTION HTML
def extract_html_content(url: str):
    """
    Extrait le contenu pertinent d'une page HTML du manuel de gestion.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de l'extraction HTML {url} : {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    header = soup.find("div", class_="entry-header")
    content = soup.find("div", class_="entry-content")

    if not content:
        return None

    text_parts = []

    if header:
        text_parts.append(header.get_text(separator=" ", strip=True))

    text_parts.append(content.get_text(separator=" ", strip=True))
    full_text = "\n".join(text_parts)
    return clean_text(full_text)
    # full_text = "\n".join(text_parts)

    # return full_text
    

# if __name__ == "__main__":
#     html_links, _ = collect_links(BASE_URL)

#     test_url = html_links[0]
#     print(f"Test extraction HTML : {test_url}")

#     extracted_text = extract_html_content(test_url)

#     if extracted_text:
#         print("Extraction réussie (extrait) :")
#         print(extracted_text[:500])
#     else:
#         print("Aucun contenu extrait")

#EXTRACTION PDF
def extract_pdf_content(pdf_url: str):
    """
    Télécharge temporairement un PDF et extrait son contenu textuel.
    """
    try:
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        print(f"PDF inaccessible (ignoré) : {pdf_url}")
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    extracted_text = []

    try:
        reader = PdfReader(tmp_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
    except Exception as e:
        print(f"Erreur lecture PDF {pdf_url} : {e}")
        return None
    finally:
        os.remove(tmp_path)

    # return "\n".join(extracted_text)
    return clean_text("\n".join(extracted_text))


# if __name__ == "__main__":
#     _, pdf_links = collect_links(BASE_URL)

#     if pdf_links:
#         test_pdf = pdf_links[0]
#         print(f"Test extraction PDF : {test_pdf}")

#         pdf_text = extract_pdf_content(test_pdf)

#         if pdf_text:
#             print("Extraction PDF réussie (extrait) :")
#             print(pdf_text[:500])
#         else:
#             print("Aucun texte extrait du PDF")

#NETTOYAGE ET NORMALISATION DU TEXTE
def clean_text(text: str) -> str:
    """
    Nettoie et normalise un texte extrait (HTML ou PDF).
    """
    if not text:
        return ""

    # Suppression des espaces multiples
    text = re.sub(r"\s+", " ", text)

    # Normalisation des sauts de ligne
    text = text.replace(" \n", "\n").replace("\n ", "\n")

    # Suppression des lignes vides
    text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

    return text.strip()
if __name__ == "__main__":
    html_links, _ = collect_links(BASE_URL)

    test_url = html_links[0]
    raw_text = extract_html_content(test_url)

    print("Texte nettoyé (extrait) :")
    print(raw_text[:500])
