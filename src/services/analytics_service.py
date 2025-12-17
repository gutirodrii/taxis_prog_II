from datetime import datetime
import pandas as pd
from typing import List, Dict, Any, Optional


class ServicioAnalisis:
    """
    Servicio encargado de procesar los datos crudos de viajes y generar
    estructuras de datos listas para ser consumidas por la vista.
    """

    @staticmethod
    def procesar_datos_destino(
        viajes: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Procesa una lista de diccionarios de viajes y devuelve un objeto consolidado
        con métricas, KPIs y datos para gráficos.

        Args:
            viajes: Lista de diccionarios representando filas del CSV.

        Returns:
            Un diccionario con las claves: 'totales', 'kpis', 'desglose', 'pago',
            'grafico', 'ultimo_registro'. Retorna None si la lista está vacía.
        """
        if not viajes:
            return None

        # --- 1. Inicialización de Acumuladores ---
        total_viajes = len(viajes)
        summ_dist = 0.0
        summ_pax = 0
        summ_coste_total_real = 0.0
        summ_duracion_horas = 0.0
        summ_duracion_minutos = 0.0

        # Acumuladores para desglose de costes
        acc_costes = {
            "Tarifa Base": 0.0,
            "Impuestos": 0.0,
            "Propinas": 0.0,
            "Peajes": 0.0,
            "Recargos": 0.0,
            "Extras/Otros": 0.0,
        }

        # Acumulador para formas de pago
        # Claves esperadas: 1 (Bizum), 2 (Efectivo), 3/4 (Otros/Desc)
        acc_pago = {}

        # --- 2. Iteración Única sobre Datos ---
        for v in viajes:
            try:
                # -- Métricas Generales --
                summ_coste_total_real += float(v.get("Importe_total", 0))
                dist = float(v.get("Distancia_KM", 0))
                summ_dist += dist
                summ_pax += int(v.get("N_pasajeros", 0))

                # -- Cálculo de Duración --
                # Formato esperado: dd/mm/YYYY HH:MM
                fmt = "%d/%m/%Y %H:%M"
                start_str = v.get("Hora_inicio")
                end_str = v.get("Hora_fin")

                if start_str and end_str:
                    try:
                        t1 = datetime.strptime(start_str, fmt)
                        t2 = datetime.strptime(end_str, fmt)
                        delta = t2 - t1
                        minutes = delta.total_seconds() / 60
                        if minutes > 0:
                            summ_duracion_minutos += minutes
                            summ_duracion_horas += minutes / 60
                    except ValueError:
                        pass

                # -- Desglose de Costes --
                # Nota: 'Tarfia_base' es un typo conocido en el CSV original
                acc_costes["Tarifa Base"] += float(v.get("Tarfia_base", 0))
                acc_costes["Impuestos"] += float(v.get("Tax", 0))
                acc_costes["Propinas"] += float(v.get("Propina", 0))
                acc_costes["Peajes"] += float(v.get("Coste_Peaje", 0))
                acc_costes["Recargos"] += float(v.get("Recargo_adicional", 0))
                acc_costes["Extras/Otros"] += float(v.get("Extra", 0))

                # -- Forma de Pago --
                try:
                    fp = int(v.get("Forma_de_pago", 0))
                except (ValueError, TypeError):
                    fp = 0

                acc_pago[fp] = acc_pago.get(fp, 0) + 1

            except (ValueError, TypeError):
                # Ignorar filas con datos corruptos numéricos críticos
                pass

        # --- 3. Cálculo de Promedios y KPIs ---
        avg_dist = summ_dist / total_viajes
        avg_pax = summ_pax / total_viajes

        # Evitar división por cero
        velocidad_media = (
            (summ_dist / summ_duracion_horas) if summ_duracion_horas > 0 else 0
        )
        coste_por_km = (summ_coste_total_real / summ_dist) if summ_dist > 0 else 0
        coste_por_min = (
            (summ_coste_total_real / summ_duracion_minutos)
            if summ_duracion_minutos > 0
            else 0
        )

        # --- 4. Análisis de Pagos ---
        bizum_count = acc_pago.get(1, 0)
        efectivo_count = acc_pago.get(2, 0)
        otros_count = acc_pago.get(3, 0) + acc_pago.get(4, 0)

        bizum_pct = bizum_count / total_viajes * 100
        efectivo_pct = efectivo_count / total_viajes * 100
        otros_pct = otros_count / total_viajes * 100

        # Determinar 'Top' Forma de Pago
        top_val = max(bizum_count, efectivo_count, otros_count)
        top_name = "N/A"
        if top_val > 0:
            if top_val == bizum_count:
                top_name = "Bizum"
            elif top_val == efectivo_count:
                top_name = "Efectivo"
            elif top_val == otros_count:
                top_name = "No ident."

        pago_info = {
            "bizum_pct": bizum_pct,
            "efectivo_pct": efectivo_pct,
            "otros_pct": otros_pct,
            "top_nombre": top_name,
        }

        # --- 5. Preparar Datos para Tabla de Desglose ---
        tabla_desglose = []
        total_desglose = sum(acc_costes.values())
        divisor_pct = total_desglose if total_desglose > 0 else 1

        for concepto, valor in acc_costes.items():
            promedio = valor / total_viajes
            porcentaje = (valor / divisor_pct) * 100
            tabla_desglose.append(
                {"concepto": concepto, "promedio": promedio, "porcentaje": porcentaje}
            )

        promedio_total_desglosado = total_desglose / total_viajes

        # --- 6. Datos para Gráficos (Pandas) ---
        # Usamos Pandas solo para facilitar el conteo y ordenamiento de categorías
        df = pd.DataFrame(viajes)
        top_origenes = None
        if "Zona_origen" in df.columns and not df.empty:
            top_origenes = df["Zona_origen"].value_counts().head(5)

        # --- Retorno Estructurado ---
        return {
            "totales": {
                "viajes": total_viajes,
                "coste": summ_coste_total_real,
                "distancia": summ_dist,
            },
            "kpis": {
                "distancia_media": avg_dist,
                "velocidad_media": velocidad_media,
                "coste_km": coste_por_km,
                "coste_min": coste_por_min,
                "pax_medio": avg_pax,
            },
            "desglose": {
                "filas": tabla_desglose,
                "total_promedio": promedio_total_desglosado,
            },
            "pago": pago_info,
            "grafico": {"top_origenes": top_origenes},
            "ultimo_registro": viajes[-1] if viajes else {},
        }
