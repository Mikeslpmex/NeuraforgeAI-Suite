import os
import json
import datetime
import subprocess

# Directorio donde guardas los reportes
REPORTS_DIR = "/ruta/a/tu/carpeta/dashboard"
# Archivo de salida del reporte diario
OUTPUT_FILE = f"/ruta/a/tu/carpeta/reporte_{datetime.date.today()}.txt"

def recolectar_reportes():
    reportes = [f for f in os.listdir(REPORTS_DIR) if f.startswith("dashboard") and f.endswith(".json")]
    return reportes

def procesar_reportes(reportes):
    total_eventos = 0
    for archivo in reportes:
        ruta = os.path.join(REPORTS_DIR, archivo)
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Aquí asumimos que cada JSON tiene un campo "eventos"
                if "eventos" in data:
                    total_eventos += len(data["eventos"])
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
    return total_eventos

def monetizar(eventos):
    # Llamada al monetizador.py con el número de eventos
    # Puedes adaptar monetizador.py para recibir este valor como argumento
    resultado = subprocess.run(["python", "monetizador.py", str(eventos)], capture_output=True, text=True)
    return resultado.stdout

if __name__ == "__main__":
    reportes = recolectar_reportes()
    total_eventos = procesar_reportes(reportes)
    monetizacion = monetizar(total_eventos)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"Fecha: {datetime.date.today()}\n")
        out.write(f"Reportes procesados: {len(reportes)}\n")
        out.write(f"Eventos totales: {total_eventos}\n")
        out.write("Resultado monetizador:\n")
        out.write(monetizacion)

    print(f"✅ Reporte generado en {OUTPUT_FILE}")
