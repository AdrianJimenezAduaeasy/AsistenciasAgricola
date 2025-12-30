from datetime import datetime
import requests
import json
from requests.exceptions import RequestException
from models.Marcacion import MarcacionDTO

# URL de ejemplo; puedes parametrizarla o actualizar las fechas según necesites
today = datetime.now().strftime("%Y-%m-%d")
api_url = f"http://127.0.0.1:8090/iclock/api/transactions/?emp_code=&start_time={today} 00:00:00&end_time={today} 23:59:59&page_size=1000"


def get_biotime_data():
    try:
        response = requests.get(
            api_url,
            headers={"Authorization": "Token 0d22b3320b5f1f0a2c34e21a37fe22fea5c2db27"})
    except RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    if response.status_code == 200:
        try:
            resp_json = response.json()

            # Normalizar a una lista de items
            if isinstance(resp_json, dict):
                # algunos endpoints envuelven la lista dentro de una clave
                # comprobamos claves habituales
                for key in ("data", "results", "transactions", "rows", "items"):
                    if key in resp_json and isinstance(resp_json[key], (list, tuple)):
                        resp_list = resp_json[key]
                        break
                else:
                    # Si el dict no contiene la lista, intentar usar sus valores
                    # o envolver el dict en una lista
                    # si el dict parece representar un objeto único, lo retornamos como lista de 1
                    resp_list = [resp_json]
            elif isinstance(resp_json, (list, tuple)):
                resp_list = resp_json
            else:
                # resp_json es un string u otro tipo; intentar parsear como JSON array
                if isinstance(resp_json, str):
                    try:
                        parsed = json.loads(resp_json)
                        resp_list = parsed if isinstance(parsed, (list, tuple)) else [parsed]
                    except Exception:
                        # no podemos parsear; devolver error
                        return {"error": "Unexpected response format"}
                else:
                    return {"error": "Unexpected response format"}

            marcaciones = []
            for item in resp_list:
                # Si el item es una cadena JSON, intentar parsearla
                if isinstance(item, str):
                    try:
                        item = json.loads(item)
                    except Exception:
                        # saltar items no parseables
                        continue

                if not isinstance(item, dict):
                    # saltar elementos que no sean dicts
                    continue

                try:
                    marc = MarcacionDTO.from_dict(item)
                    # devolver la instancia dataclass para que el código interno la use como objeto
                    marcaciones.append(marc)
                except Exception:
                    # si falla el parseo de un elemento, saltarlo
                    continue

            return marcaciones
        except ValueError:
            return {"error": "Invalid JSON in response"}
    else:
        return {"error": f"Failed to retrieve data, status code: {response.status_code}"}