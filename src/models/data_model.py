import csv
import os
from typing import List, Dict, Any

class ModeloDatos:
    """
    Modelo para gestionar la carga y acceso a los datos del archivo CSV.
    Almacena los registros en memoria como una lista de diccionarios.
    """
    def __init__(self):
        self._datos: List[Dict[str, Any]] = []
        self._cabeceras: List[str] = []

    def cargar_datos(self, ruta_archivo: str) -> None:
        """
        Carga datos desde un archivo CSV a memoria.
        
        Args:
            ruta_archivo: Ruta absoluta o relativa al archivo .csv.
            
        Raises:
            FileNotFoundError: Si el archivo no existe.
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
            
        with open(ruta_archivo, mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            if lector.fieldnames:
                self._cabeceras = list(lector.fieldnames)
            self._datos = list(lector)

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Devuelve todos los registros cargados."""
        return self._datos

    def obtener_cabeceras(self) -> List[str]:
        """Devuelve la lista de nombres de columnas del CSV."""
        return self._cabeceras

    def obtener_destinos_unicos(self) -> List[str]:
        """
        Extrae y devuelve una lista ordenada alfabéticamente de
        todos los destinos únicos ('Zona_destino') presentes en los datos.
        """
        # Usamos un set comprehension para velocidad y unicidad
        destinos = {item.get('Zona_destino') for item in self._datos if item.get('Zona_destino')}
        return sorted(list(destinos))

    def obtener_viajes_por_destino(self, destino: str) -> List[Dict[str, Any]]:
        """
        Filtra y devuelve todos los viajes que coinciden con el destino dado.
        """
        return [item for item in self._datos if item.get('Zona_destino') == destino]
