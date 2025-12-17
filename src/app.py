import tkinter as tk
from src.config import Configuracion
from src.views.styles import configurar_estilos
from src.views.main_view import VistaPrincipal
from src.models.data_model import ModeloDatos
from src.controllers.main_controller import ControladorPrincipal

class Aplicacion:
    """
    Envoltorio principal de la aplicación.
    Responsable de inicializar la ventana raíz, estilos y los componentes MVC principales.
    """
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self._configurar_ventana()
        self._configurar_estilos()
        self._iniciar_app()

    def _configurar_ventana(self):
        self.raiz.title(Configuracion.TITULO_APP)
        self.raiz.geometry(Configuracion.TAMANO_VENTANA)
        if not Configuracion.REDIMENSIONABLE:
            self.raiz.resizable(False, False)
        # Color de fondo para la ventana raíz
        self.raiz.configure(bg=Configuracion.COLOR_FONDO_APP)

    def _configurar_estilos(self):
        configurar_estilos()

    def _iniciar_app(self):
        # Inicializar Modelo, Vista y Controlador
        
        # 1. Crear Modelo
        modelo = ModeloDatos()
        
        # 2. Crear Vista (y empaquetarla en raíz)
        vista = VistaPrincipal(self.raiz)
        vista.pack(expand=True, fill="both")
        
        # 3. Crear Controlador (inyecta modelo y vista)
        controlador = ControladorPrincipal(modelo, vista)
