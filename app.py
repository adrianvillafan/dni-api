from fastapi import FastAPI, HTTPException
import requests as r
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/obtener_datos_dni/")
def obtener_datos_dni(dni: str):
    if len(dni) != 8 or not dni.isdigit():
        raise HTTPException(status_code=400, detail="El DNI debe tener 8 dígitos")

    # Obtención de cookies
    s = r.Session()
    res1 = s.get("https://dni-peru.com/buscar-dni-nombres-apellidos/")

    # Envío de información
    res2 = s.post("https://dni-peru.com/buscar-dni-nombres-apellidos/", data={'dni4': dni, 'buscar_dni': ''})

    # Obtención de variables
    soup = BeautifulSoup(res2.text, 'html.parser')
    div = soup.find('div', {'id': 'resultado_busqueda'})
    datos = div.find_all('p', recursive=True)

    try:
        bs_nombre = BeautifulSoup(str(datos[2]), 'html.parser')
        p_nombre = bs_nombre.find('p')
        nombre = ''.join(p_nombre.find_all(string=True, recursive=False))

        bs_paterno = BeautifulSoup(str(datos[3]), 'html.parser')
        p_paterno = bs_paterno.find('p')
        paterno = ''.join(p_paterno.find_all(string=True, recursive=False))

        bs_materno = BeautifulSoup(str(datos[4]), 'html.parser')
        p_materno = bs_materno.find('p')
        materno = ''.join(p_materno.find_all(string=True, recursive=False))

        return {
            "nombres": nombre.strip(),
            "apellido_paterno": paterno.strip(),
            "apellido_materno": materno.strip()
        }
    except:
        raise HTTPException(status_code=500, detail="Error al obtener los datos")

