import numpy as np
import pdfplumber
import pandas as pd
import re

def cargar_pdf(ruta_pdf: str):
    f = open(ruta_pdf, "rb")
    pdf = pdfplumber.open(f)
    return pdf, f

def extraer_texto_paginas(pdf) -> str:
    texto = ""
    for p in pdf.pages:
        contenido = p.extract_text()
        if contenido:
            texto += contenido + "\n"
    return texto

def limpiar_lineas(texto: str) -> list:
    lineas = [line.strip() for line in texto.split("\n") if line.strip()]
    return lineas

def extraer_transacciones(lineas: list) -> pd.DataFrame:
    patron = re.compile(
        r"(\d{2}/\d{2})\s+(.*?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})"
    )

    registros = []
    for linea in lineas:
        match = patron.search(linea)
        if match:
            fecha, establecimiento, valor = match.groups()
            registros.append({
                "fecha": fecha,
                "establecimiento": establecimiento,
                "valor": float(valor.replace(".", "").replace(",", "."))
            })

    return pd.DataFrame(registros)

def cargar_estado_cuenta(ruta_pdf: str) -> pd.DataFrame:
    pdf, f = cargar_pdf(ruta_pdf)
    texto = extraer_texto_paginas(pdf)
    lineas = limpiar_lineas(texto)
    df = extraer_transacciones(lineas)
    pdf.close()
    f.close()
    return df