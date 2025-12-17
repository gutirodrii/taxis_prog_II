import json
import csv
from typing import Dict, Any


class ServicioExportacion:
    """
    Servicio encargado de exportar los datos analizados a diferentes formatos.
    """

    @staticmethod
    def exportar_csv(datos: Dict[str, Any], ruta_archivo: str):
        """Genera un CSV plano con los KPIs principales y el desglose de costes."""
        encabezados = [
            "Viajes",
            "Coste Total",
            "Distancia Media",
            "Velocidad Media",
            "Coste/Km",
            "Coste/Min",
            "Pax Medio",
            "Top Pago",
            "Concepto Desglose",
            "Importe Desglose",
        ]

        # Aplanar datos para una fila por concepto de desglose
        filas = []
        totales = datos["totales"]
        kpis = datos["kpis"]
        pago = datos["pago"]

        base_row = {
            "Viajes": totales["viajes"],
            "Coste Total": totales["coste"],
            "Distancia Media": kpis["distancia_media"],
            "Velocidad Media": kpis["velocidad_media"],
            "Coste/Km": kpis["coste_km"],
            "Coste/Min": kpis["coste_min"],
            "Pax Medio": kpis["pax_medio"],
            "Top Pago": pago["top_nombre"],
        }

        for item in datos["desglose"]["filas"]:
            fila = base_row.copy()
            fila["Concepto Desglose"] = item["concepto"]
            fila["Importe Desglose"] = item["promedio"]
            filas.append(fila)

        with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=encabezados)
            writer.writeheader()
            writer.writerows(filas)

    @staticmethod
    def exportar_json(datos: Dict[str, Any], ruta_archivo: str):
        """Exporta el diccionario completo de datos a JSON."""
        # Convertir objetos no serializables si los hubiera (como DataFrames de pandas),
        # pero 'datos' ya viene limpio del servicio de análisis.
        # Eliminamos 'grafico' que puede contener DataFrames o Series
        datos_safe = datos.copy()
        if "grafico" in datos_safe:
            del datos_safe["grafico"]

        # El ultimo registro puede ser registro crudo del CSV, es serializable.
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos_safe, f, indent=4, ensure_ascii=False)

    @staticmethod
    def exportar_md(datos: Dict[str, Any], ruta_archivo: str, destino: str):
        """Genera un reporte legible en Markdown."""
        kpis = datos["kpis"]
        totales = datos["totales"]
        pago = datos["pago"]

        md = f"""# Reporte de Análisis: {destino}
        
## Resumen Ejecutivo
- **Total Viajes**: {totales["viajes"]}
- **Coste Total**: ${totales["coste"]:,.2f}
- **Distancia Acumulada**: {totales["distancia"]:,.2f} km

## KPIs
| Métrica | Valor |
|---------|-------|
| Distancia Media | {kpis["distancia_media"]:.2f} km |
| Velocidad Media | {kpis["velocidad_media"]:.1f} km/h |
| Coste / Km | ${kpis["coste_km"]:.2f} |
| Coste / Min | ${kpis["coste_min"]:.2f} |
| Pax / Viaje | {kpis["pax_medio"]:.1f} |

## Análisis de Pago
- **Método Preferido**: {pago["top_nombre"]}
- **Bizum**: {pago["bizum_pct"]:.1f}%
- **Efectivo**: {pago["efectivo_pct"]:.1f}%

## Desglose de Costes (Promedio)
| Concepto | Coste ($) | % Total |
|----------|-----------|---------|
"""
        for item in datos["desglose"]["filas"]:
            md += f"| {item['concepto']} | ${item['promedio']:.2f} | {item['porcentaje']:.1f}% |\n"

        md += f"| **TOTAL** | **${datos['desglose']['total_promedio']:.2f}** | **100%** |\n"

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(md)

    @staticmethod
    def exportar_csv_global(lista_datos: list, ruta_archivo: str):
        """Genera un CSV con una fila por destino (resumen global)."""
        encabezados = [
            "Destino",
            "Viajes",
            "Coste Total",
            "Distancia Media",
            "Velocidad Media",
            "Coste/Km",
            "Coste/Min",
            "Pax Medio",
            "Top Pago",
            "Pago Top %",
        ]

        filas = []
        for datos in lista_datos:
            kpis = datos["kpis"]
            totales = datos["totales"]
            pago = datos["pago"]

            top_key = (
                pago["top_nombre"].lower() if pago["top_nombre"] != "N/A" else "otros"
            )
            # Mapear nombre top a su porcentaje usando las keys estandarizadas
            pct_key = (
                "bizum_pct"
                if "bizum" in top_key
                else ("efectivo_pct" if "efectivo" in top_key else "otros_pct")
            )
            pct_val = pago.get(pct_key, 0)

            filas.append(
                {
                    "Destino": datos.get("destino_nombre", "N/A"),
                    "Viajes": totales["viajes"],
                    "Coste Total": totales["coste"],
                    "Distancia Media": kpis["distancia_media"],
                    "Velocidad Media": kpis["velocidad_media"],
                    "Coste/Km": kpis["coste_km"],
                    "Coste/Min": kpis["coste_min"],
                    "Pax Medio": kpis["pax_medio"],
                    "Top Pago": pago["top_nombre"],
                    "Pago Top %": pct_val,
                }
            )

        with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=encabezados)
            writer.writeheader()
            writer.writerows(filas)

    @staticmethod
    def exportar_json_global(lista_datos: list, ruta_archivo: str):
        """Exporta la lista completa de datos de todos los destinos a JSON."""
        # Limpiar datos no serializables (graficos) de cada entrada
        datos_limpios = []
        for d in lista_datos:
            d_safe = d.copy()
            if "grafico" in d_safe:
                del d_safe["grafico"]
            datos_limpios.append(d_safe)

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos_limpios, f, indent=4, ensure_ascii=False)

    @staticmethod
    def exportar_png(figura, ruta_archivo: str):
        """Guarda la figura de matplotlib pasada como argumento."""
        if figura:
            figura.savefig(ruta_archivo, bbox_inches="tight", dpi=150)
