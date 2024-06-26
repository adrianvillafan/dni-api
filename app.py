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
        # Obtención de cookies
        s = requests.Session()
        res1 = s.get("https://dni-peru.com/buscar-dni-nombres-apellidos/")
        if res1.status_code != 200:
            raise Exception(f"Error al obtener cookies: {res1.status_code}")
        
        # Envío de información
        res2 = s.post("https://dni-peru.com/buscar-dni-nombres-apellidos/", data={'dni4': dni, 'buscar_dni': ''})
        if res2.status_code != 200:
            raise Exception(f"Error al enviar datos: {res2.status_code}")

        # Obtención de variables
        soup = BeautifulSoup(res2.text, 'html.parser')

        # Depuración: imprimir el HTML completo recibido
        html_content = soup.prettify()
        print(html_content)

        div = soup.find('div', {'id': 'resultado_busqueda'})
        if not div:
            raise Exception("No se encontró el div de resultado de búsqueda")
        
        datos = div.find_all('p', recursive=True)
        if len(datos) < 5:
            raise Exception("No se encontraron suficientes datos en el resultado de búsqueda")

        try:
            bs_nombre = BeautifulSoup(str(datos[2]), 'html.parser')
            p_nombre = bs_nombre.find('p')
            nombre = ''.join(p_nombre.find_all(string=True, recursive=False)).strip()

            bs_paterno = BeautifulSoup(str(datos[3]), 'html.parser')
            p_paterno = bs_paterno.find('p')
            paterno = ''.join(p_paterno.find_all(string=True, recursive=False)).strip()

            bs_materno = BeautifulSoup(str(datos[4]), 'html.parser')
            p_materno = bs_materno.find('p')
            materno = ''.join(p_materno.find_all(string=True, recursive=False)).strip()

            return jsonify({
                "nombres": nombre.strip(),
                "apellido_paterno": paterno.strip(),
                "apellido_materno": materno.strip()
            })
        except Exception as e:
            raise Exception(f"Error procesando los datos: {str(e)}")
    except Exception as e:
        return jsonify({"detail": f"Error al obtener los datos: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
