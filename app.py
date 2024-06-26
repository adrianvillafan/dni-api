from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/obtener_datos_dni/", methods=["GET"])
def obtener_datos_dni():
    dni = request.args.get('dni')
    if not dni or len(dni) != 8 or not dni.isdigit():
        return jsonify({"detail": "El DNI debe tener 8 dígitos"}), 400

    try:
        # Agregar encabezados para la solicitud
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-419,es;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://eldni.com',
            'Referer': 'https://eldni.com/pe/buscar-por-dni',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Gpc': '1'
        }

        # Obtención de cookies y del token
        s = requests.Session()
        res1 = s.get("https://eldni.com/pe/buscar-por-dni", headers=headers)
        if res1.status_code != 200:
            raise Exception(f"Error al obtener cookies: {res1.status_code}")
        
        # Parsear el contenido HTML para obtener el token
        soup = BeautifulSoup(res1.text, 'html.parser')
        token = soup.find('input', {'name': '_token'}).get('value')
        if not token:
            raise Exception("No se encontró el token en el HTML")

        # Envío de información
        headers['Content-Type'] = 'multipart/form-data; boundary=----WebKitFormBoundarybDEpouvEPBTsaBvw'
        cookies = res1.cookies.get_dict()
        
        payload = {
            '_token': token,
            'dni': dni
        }
        
        res2 = s.post("https://eldni.com/pe/buscar-datos-por-dni", 
                      headers=headers,
                      cookies=cookies,
                      data=payload)
        if res2.status_code != 200:
            raise Exception(f"Error al enviar datos: {res2.status_code}")

        # Parsear el HTML de la respuesta
        soup = BeautifulSoup(res2.text, 'html.parser')
        table = soup.find('table', {'class': 'table table-striped table-scroll'})
        if not table:
            raise Exception("No se encontró la tabla de resultados")

        # Extraer los datos de la tabla
        rows = table.find_all('tr')
        if len(rows) < 2:
            raise Exception("No se encontraron suficientes filas en la tabla de resultados")

        cols = rows[1].find_all('td')
        if len(cols) < 4:
            raise Exception("No se encontraron suficientes columnas en la fila de resultados")

        nombre = cols[1].text.strip()
        apellido_paterno = cols[2].text.strip()
        apellido_materno = cols[3].text.strip()

        return jsonify({
            "nombres": nombre,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno
        })
    except Exception as e:
        return jsonify({"detail": f"Error al obtener los datos: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
