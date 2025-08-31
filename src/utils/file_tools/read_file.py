import asyncio
import fitz
import easyocr
import numpy as np
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm

executor = ThreadPoolExecutor(max_workers=1)

def is_scanned_pdf(path: str) -> bool:
    """
    Détermine si un fichier PDF donné est un document scanné sans texte intégré.

    Cette fonction ouvre le fichier PDF spécifié et vérifie chaque page pour la présence
    de texte. Si une page contient du texte, le PDF n'est pas considéré comme un document
    scanné. Si aucun texte n'est trouvé sur toutes les pages, le PDF est classé comme un
    document scanné.

    Args:
        path (str): Le chemin du fichier vers le document PDF à analyser.

    Returns:
        bool: True si le PDF est un document scanné sans texte intégré, False sinon.
    """
    with fitz.open(path) as pdf:
        for page in pdf:
            if page.get_text().strip():
                return False
    return True

async def read_pdf_text_async(path: str):
    """Async generator pour lire un PDF textuel"""
    with fitz.open(path) as pdf:
        total_pages = len(pdf)
        loop = asyncio.get_event_loop()
        with tqdm(total=total_pages, desc="Reading text PDF", unit="page") as pbar:
            for i in range(total_pages):
                page_text = await loop.run_in_executor(executor, lambda i=i: pdf[i].get_text())
                pbar.update(1)
                yield page_text

async def read_pdf_scan_async(path: str):
    """
    Lit un PDF scanné (OCR avec EasyOCR) page par page.
    `poppler_path` nécessaire sur Windows si Poppler n'est pas dans le PATH.
    """
    loop = asyncio.get_event_loop()
    reader = easyocr.Reader(['fr', 'en'])

    pages = await loop.run_in_executor(
        executor,
        lambda: convert_from_path(path, dpi=300, poppler_path=r"C:\poppler\Library\bin") 
    )
    with tqdm(total=len(pages), desc="Reading scanned PDF", unit="page") as pbar:
        for page in pages:
            img_np = np.array(page)
            results = await loop.run_in_executor(executor, lambda img=img_np: reader.readtext(img))
            lines = []
            current_y = None
            current_line = []
            
            sorted_results = sorted(results, key=lambda x: (x[0][0][1], x[0][0][0]))
            
            for bbox, text, ratio in sorted_results:
                if ratio > 0.3:
                    top_y = bbox[0][1]
                    if current_y is None:
                        current_y = top_y
                    
                    if abs(top_y - current_y) > 10:
                        lines.append(" ".join(current_line))
                        current_line = [text]
                        current_y = top_y
                    else:
                        current_line.append(text)
            
            if current_line:
                lines.append(" ".join(current_line))
            
            page_text = "\n".join(lines)
            pbar.update(1)
            yield page_text

async def read_file_async(path: str):
    """Détecte si le PDF est texte ou scan, et lit en conséquence"""
    if is_scanned_pdf(path):
        async for page in read_pdf_scan_async(path):
            yield page
    else:
        async for page in read_pdf_text_async(path):
            yield page