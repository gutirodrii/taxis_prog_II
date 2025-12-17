import os
import tkinter as tk
from tkinter import filedialog
from src.models.data_model import ModeloDatos
from src.views.main_view import VistaPrincipal
from src.services.analytics_service import ServicioAnalisis
from src.services.export_service import ServicioExportacion


class ControladorPrincipal:
    """
    Controlador que gestiona la lógica de interacción entre la Vista y el Modelo.
    Maneja la carga de datos, la navegación, la selección de destinos y la exportación.
    """

    def __init__(self, modelo: ModeloDatos, vista: VistaPrincipal):
        self.modelo = modelo
        self.vista = vista
        self._timer_id = None
        self.datos_actuales = None  # Cache de datos analizados

        # Vincular la acción del botón 'Entrar'
        self.vista.btn_entrar.config(command=self.entrar_panel)

    def entrar_panel(self):
        """Transición de la pantalla de bienvenida al panel principal."""
        self.vista.mostrar_panel()
        self.vista.lista_destinos.bind(
            "<<ListboxSelect>>", self.manejar_seleccion_destino
        )
        self.cargar_datos_y_destinos()

    def cargar_datos_y_destinos(self):
        """Orquesta la carga del archivo CSV y actualiza la lista lateral."""
        try:
            ruta_csv = os.path.join(os.getcwd(), "data", "NYC_202501.csv")

            if not self.modelo.obtener_todos():
                self.modelo.cargar_datos(ruta_csv)

            destinos = self.modelo.obtener_destinos_unicos()
            self.vista.actualizar_lista_destinos(destinos)

        except FileNotFoundError:
            print("Error: No se encontró el archivo de datos 'NYC_202501.csv'.")
        except Exception as e:
            print(f"Error inesperado cargando datos: {e}")

    def manejar_seleccion_destino(self, evento: tk.Event):
        """Handler para el evento de selección con debounce."""
        if self._timer_id:
            self.vista.after_cancel(self._timer_id)
        self._timer_id = self.vista.after(250, self._actualizar_vista)

    def _actualizar_vista(self):
        """Calcula el análisis y actualiza la vista con los nuevos datos."""
        self._timer_id = None

        seleccion = self.vista.lista_destinos.curselection()
        if seleccion:
            index = seleccion[0]
            destino = self.vista.lista_destinos.get(index)

            # 1. Obtener viajes crudos
            viajes = self.modelo.obtener_viajes_por_destino(destino)

            # 2. Procesar métricas en el controlador
            datos = ServicioAnalisis.procesar_datos_destino(viajes)
            if not datos:
                return

            self.datos_actuales = datos
            self.datos_actuales["destino_nombre"] = (
                destino  # Guardar nombre para reportes
            )

            # 3. Preparar callbacks de exportación
            # Nota: CSV y JSON ahora son GLOBALES, MD y PNG son ACTUALES
            callbacks = {
                "csv": lambda: self.exportar_global("csv"),
                "json": lambda: self.exportar_global("json"),
                "md": lambda: self.exportar_actual("md"),
                "png": lambda: self.exportar_actual("png"),
            }

            # 4. Actualizar UI
            self.vista.mostrar_analisis(destino, datos, callbacks)

    def exportar_actual(self, formato: str):
        """Exporta los datos del destino ACTUALMENTE seleccionado (MD, PNG)."""
        if not self.datos_actuales:
            return

        filtro = ""
        ext = ""
        if formato == "md":
            filtro, ext = "Archivos Markdown (*.md)", ".md"
        elif formato == "png":
            filtro, ext = "Imagen PNG (*.png)", ".png"
        else:
            return

        destino_safe = self.datos_actuales.get("destino_nombre", "Destino").replace(
            " ", "_"
        )

        archivo = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=f"Reporte_{destino_safe}{ext}",
            filetypes=[
                (filtro.split(" (")[0], f"*{ext}"),
                ("Todos los archivos", "*.*"),
            ],
            title=f"Exportar reporte actual como {formato.upper()}",
        )

        if not archivo:
            return

        try:
            if formato == "md":
                ServicioExportacion.exportar_md(
                    self.datos_actuales,
                    archivo,
                    self.datos_actuales.get("destino_nombre", "Destino"),
                )
            elif formato == "png":
                fig = self.vista.figura_actual
                if fig:
                    ServicioExportacion.exportar_png(fig, archivo)

            print(f"Exportación actual a {archivo} completada.")
        except Exception as e:
            print(f"Error exportando actual: {e}")

    def exportar_global(self, formato: str):
        """Exporta los datos de TODOS los destinos (CSV, JSON)."""
        filtro = ""
        ext = ""
        if formato == "csv":
            filtro, ext = "Archivos CSV (*.csv)", ".csv"
        elif formato == "json":
            filtro, ext = "Archivos JSON (*.json)", ".json"
        else:
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=f"Reporte_Global{ext}",
            filetypes=[
                (filtro.split(" (")[0], f"*{ext}"),
                ("Todos los archivos", "*.*"),
            ],
            title=f"Exportar reporte GLOBAL como {formato.upper()}",
        )

        if not archivo:
            return

        try:
            # Procesar todos los destinos (puede tardar un poco)
            datos_globales = self._obtener_datos_todos_destinos()

            if formato == "csv":
                ServicioExportacion.exportar_csv_global(datos_globales, archivo)
            elif formato == "json":
                ServicioExportacion.exportar_json_global(datos_globales, archivo)

            print(f"Exportación global a {archivo} completada.")
        except Exception as e:
            print(f"Error exportando global: {e}")

    def _obtener_datos_todos_destinos(self):
        """Itera sobre todos los destinos y genera sus métricas."""
        todos_datos = []
        destinos = self.modelo.obtener_destinos_unicos()

        for d in destinos:
            viajes = self.modelo.obtener_viajes_por_destino(d)
            if viajes:
                datos = ServicioAnalisis.procesar_datos_destino(viajes)
                if datos:
                    datos["destino_nombre"] = d
                    todos_datos.append(datos)

        return todos_datos
