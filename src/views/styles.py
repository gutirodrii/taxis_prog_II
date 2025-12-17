from tkinter import ttk
from src.config import Configuracion

def configurar_estilos():
    """Configura estilos ttk personalizados para una apariencia profesional."""
    estilo = ttk.Style()
    
    try:
        estilo.theme_use('clam')
    except:
        pass

    # --- Frames ---
    estilo.configure("App.TFrame", background=Configuracion.COLOR_FONDO_APP)
    estilo.configure("Panel.TFrame", background=Configuracion.COLOR_PANEL_LATERAL)
    
    # --- Labels ---
    estilo.configure("Titulo.TLabel", background=Configuracion.COLOR_FONDO_APP, foreground=Configuracion.COLOR_TEXTO_PRINCIPAL, font=(Configuracion.FUENTE_FAMILIA, Configuracion.TAMANO_TITULO_GRANDE, "bold"))
    estilo.configure("TituloPanel.TLabel", background=Configuracion.COLOR_PANEL_LATERAL, foreground=Configuracion.COLOR_TEXTO_PRINCIPAL, font=(Configuracion.FUENTE_FAMILIA, 18, "bold"))
    estilo.configure("Normal.TLabel", background=Configuracion.COLOR_PANEL_LATERAL, foreground=Configuracion.COLOR_TEXTO_PRINCIPAL, font=(Configuracion.FUENTE_FAMILIA, Configuracion.TAMANO_TEXTO))
    estilo.configure("Secundario.TLabel", background=Configuracion.COLOR_PANEL_LATERAL, foreground=Configuracion.COLOR_TEXTO_SECUNDARIO, font=(Configuracion.FUENTE_FAMILIA, Configuracion.TAMANO_TEXTO))
    estilo.configure("KPI.Label.TLabel", background=Configuracion.COLOR_TARJETA, foreground=Configuracion.COLOR_TEXTO_SECUNDARIO, font=(Configuracion.FUENTE_FAMILIA, 10, "bold"))
    estilo.configure("KPI.Value.TLabel", background=Configuracion.COLOR_TARJETA, foreground=Configuracion.COLOR_PRIMARIO, font=(Configuracion.FUENTE_FAMILIA, Configuracion.TAMANO_KPI, "bold"))

    # --- Botones ---
    estilo.configure("Primario.TButton", background=Configuracion.COLOR_PRIMARIO, foreground="white", font=(Configuracion.FUENTE_FAMILIA, 12, "bold"), borderwidth=0, focuscolor="none", padding=10)
    estilo.map("Primario.TButton", background=[('active', Configuracion.COLOR_PRIMARIO_HOVER)])

    # --- Treeview (Tablas Estilo Excel) ---
    estilo.configure("Treeview", 
        background="white",
        fieldbackground="white",
        foreground=Configuracion.COLOR_TEXTO_PRINCIPAL,
        font=(Configuracion.FUENTE_FAMILIA, 11),
        rowheight=25,
        borderwidth=0
    )
    estilo.configure("Treeview.Heading", 
        font=(Configuracion.FUENTE_FAMILIA, 10, "bold"),
        background=Configuracion.COLOR_FONDO_APP,
        foreground=Configuracion.COLOR_TEXTO_SECUNDARIO,
        relief="flat"
    )
    estilo.map("Treeview", background=[('selected', '#e0f2fe')], foreground=[('selected', Configuracion.COLOR_PRIMARIO)]) # Selección azul muy suave
    
    # Separador
    estilo.configure("Horizontal.TSeparator", background=Configuracion.COLOR_BORDE)
