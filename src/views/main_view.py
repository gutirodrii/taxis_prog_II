import tkinter as tk
from tkinter import ttk
from src.config import Configuracion
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import seaborn as sns


class VistaPrincipal(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, style="App.TFrame")  # Fondo App
        self.padre = padre
        self.pack(fill="both", expand=True)

        # Layout principal
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.marco_actual = None
        self.mostrar_bienvenida()

    def mostrar_bienvenida(self):
        """Pantalla de bienvenida limpia y centrada."""
        if self.marco_actual:
            self.marco_actual.destroy()

        self.marco_actual = ttk.Frame(self, style="App.TFrame")
        self.marco_actual.grid(row=0, column=0, sticky="nsew")
        self.marco_actual.columnconfigure(0, weight=1)
        self.marco_actual.rowconfigure(0, weight=1)

        # Caja centrada (tarjeta blanca)
        caja = ttk.Frame(self.marco_actual, style="Panel.TFrame", padding=40)
        caja.grid(row=0, column=0)

        # Sombra simulada (borde)
        caja.configure(borderwidth=1, relief="solid")  # Borde fino

        lbl_titulo = ttk.Label(
            caja, text=Configuracion.TITULO_APP, style="TituloPanel.TLabel"
        )
        lbl_titulo.pack(pady=(0, 20))

        lbl_sub = ttk.Label(
            caja,
            text="Análisis de datos de transporte urbano",
            style="Secundario.TLabel",
        )
        lbl_sub.pack(pady=(0, 30))

        self.btn_entrar = ttk.Button(
            caja, text="Iniciar Dashboard", style="Primario.TButton", cursor="hand2"
        )
        self.btn_entrar.pack(ipadx=30, ipady=10)

    def mostrar_panel(self):
        """Panel principal con Sidebar y Área de Contenido."""
        if self.marco_actual:
            self.marco_actual.destroy()

        self.marco_actual = ttk.Frame(self, style="App.TFrame")
        self.marco_actual.grid(row=0, column=0, sticky="nsew")

        # Split: Sidebar (Izquierda) vs Contenido (Derecha)
        # Usamos PanedWindow pero estilizado si es posible, o frames manuales para controlar colores.
        # PanedWindow nativo a veces es feo. Usaremos Grid simple.

        self.marco_actual.columnconfigure(0, weight=1, minsize=250)  # Sidebar
        self.marco_actual.columnconfigure(1, weight=4)  # Contenido
        self.marco_actual.rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ttk.Frame(self.marco_actual, style="Panel.TFrame", padding=20)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Borde derecho sidebar
        sep = ttk.Separator(self.sidebar, orient="vertical")
        sep.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        ttk.Label(
            self.sidebar,
            text="Destinos",
            style="TituloPanel.TLabel",
            font=(Configuracion.FUENTE_FAMILIA, 14, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        # Listbox personalizado
        self.lista_destinos = tk.Listbox(
            self.sidebar,
            bg=Configuracion.COLOR_PANEL_LATERAL,
            fg=Configuracion.COLOR_TEXTO_PRINCIPAL,
            bd=0,
            highlightthickness=0,
            selectbackground=Configuracion.COLOR_PRIMARIO,
            selectforeground="white",
            activestyle="none",
            font=(Configuracion.FUENTE_FAMILIA, 12),
            cursor="hand2",
        )
        self.lista_destinos.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(
            self.sidebar, orient="vertical", command=self.lista_destinos.yview
        )
        sb.pack(side="right", fill="y")
        self.lista_destinos.config(yscrollcommand=sb.set)

        # --- CONTENIDO (DERECHA) ---
        self.content_area = ttk.Frame(self.marco_actual, style="App.TFrame", padding=30)
        self.content_area.grid(row=0, column=1, sticky="nsew")

        # Header del contenido
        self.header_frame = ttk.Frame(self.content_area, style="App.TFrame")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.lbl_titulo_analisis = ttk.Label(
            self.header_frame, text="Dashboard", style="Titulo.TLabel"
        )
        self.lbl_titulo_analisis.pack(anchor="w")

        self.lbl_subtitulo_analisis = ttk.Label(
            self.header_frame,
            text="Selecciona un destino para comenzar",
            style="Secundario.TLabel",
        )
        self.lbl_subtitulo_analisis.pack(anchor="w")

        # Contenedor del informe (Scrollable si hiciera falta, pero con layout limpio quizas no)
        # Vamos a usar un Frame blanco "Tarjeta" para el reporte
        self.report_card = ttk.Frame(
            self.content_area, style="Panel.TFrame", padding=30
        )
        self.report_card.pack(fill="both", expand=True)

        # Placeholder
        self.lbl_placeholder = ttk.Label(
            self.report_card, text="Waiting for selection...", style="Secundario.TLabel"
        )
        self.lbl_placeholder.pack(expand=True)

    def actualizar_lista_destinos(self, destinos):
        self.lista_destinos.delete(0, tk.END)
        for d in destinos:
            self.lista_destinos.insert(tk.END, d)

    def mostrar_analisis(self, destino: str, datos: dict, callbacks: dict = None):
        """
        Orquesta la renderización del dashboard.

        Args:
            destino: Nombre del destino seleccionado.
            datos: Diccionario de datos ya procesados por el servicio.
            callbacks: Diccionario de funciones para acciones (exportar, etc).
        """
        # Limpiar dashboard anterior
        self.figura_actual = None  # Reset figura
        plt.close("all")
        for w in self.report_card.winfo_children():
            w.destroy()

        # Actualizar Título Principal
        viajes_count = datos["totales"]["viajes"]
        self.lbl_titulo_analisis.config(text=destino)
        self.lbl_subtitulo_analisis.config(
            text=f"Reporte de actividad • {viajes_count} viajes registrados"
        )

        # --- Layout Principal (Grid 2x2 + Botonera) ---
        contenedor = ttk.Frame(self.report_card, style="Panel.TFrame")
        contenedor.pack(fill="both", expand=True)

        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=0)  # Gráfico + Top KPIs
        contenedor.rowconfigure(1, weight=1)  # Tablas / Detalles
        contenedor.rowconfigure(2, weight=0)  # Botonera Exportación
        contenedor.rowconfigure(3, weight=0)  # Footer

        # 1. Renderizar Componentes
        self._renderizar_grafico(contenedor, datos["grafico"]["top_origenes"])
        self._renderizar_kpis_top(contenedor, datos["totales"], datos["kpis"])
        self._renderizar_panel_inferior(
            contenedor, datos["kpis"], datos["pago"], datos["desglose"]
        )

        # 2. Renderizar Botones de Exportación (Mosaico)
        if callbacks:
            self._renderizar_botones_exportacion(contenedor, callbacks)

        # 3. Renderizar Footer
        self._renderizar_footer(contenedor, datos["ultimo_registro"])

    def _renderizar_botones_exportacion(self, parent, callbacks):
        """Crea dos grupos de botones para exportación (Global vs Actual) apilados verticalmente."""
        frame_btns = ttk.Frame(parent, style="Panel.TFrame")
        # Cambio IMPORTANTE: columnspan=1 para que se quede en la columna izquierda
        frame_btns.grid(
            row=2, column=0, columnspan=1, sticky="ew", pady=(20, 0), padx=(0, 20)
        )

        frame_btns.columnconfigure(0, weight=1)

        # --- GRUPO SUPERIOR: GLOBAL ---
        f_global = ttk.Frame(frame_btns, style="Panel.TFrame")
        f_global.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(
            f_global, text="Exportar informe global:", style="KPI.Label.TLabel"
        ).pack(anchor="w", pady=(0, 5))

        # Grid de botones global
        fg_btns = ttk.Frame(f_global, style="Panel.TFrame")
        fg_btns.pack(fill="x")
        fg_btns.columnconfigure(0, weight=1)
        fg_btns.columnconfigure(1, weight=1)

        self._crear_boton_export(fg_btns, 0, "CSV", "csv", "📄", callbacks)
        self._crear_boton_export(fg_btns, 1, "JSON", "json", "｛ ｝", callbacks)

        # --- GRUPO INFERIOR: ACTUAL ---
        f_actual = ttk.Frame(frame_btns, style="Panel.TFrame")
        f_actual.grid(row=1, column=0, sticky="ew")

        ttk.Label(
            f_actual, text="Enviar informe actual:", style="KPI.Label.TLabel"
        ).pack(anchor="w", pady=(0, 5))

        # Grid de botones actual
        fa_btns = ttk.Frame(f_actual, style="Panel.TFrame")
        fa_btns.pack(fill="x")
        fa_btns.columnconfigure(0, weight=1)
        fa_btns.columnconfigure(1, weight=1)

        self._crear_boton_export(fa_btns, 0, "Markdown", "md", "M↓", callbacks)
        self._crear_boton_export(fa_btns, 1, "Imagen", "png", "🖼", callbacks)

    def _crear_boton_export(self, parent, col, text, key, icon, callbacks):
        """Helper par crear un botón de exportación individual."""

        def cmd():
            return callbacks.get(key, lambda: None)()

        btn = ttk.Button(
            parent, text=f"{icon} {text}", command=cmd, style="Primario.TButton"
        )
        btn.grid(row=0, column=col, sticky="ew", padx=5)

    def _renderizar_grafico(self, parent, top_data):
        """Genera el gráfico de barras en el cuadrante superior izquierdo."""
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=(0, 20))

        ttk.Label(
            frame,
            text="Top Zonas de Origen",
            style="TituloPanel.TLabel",
            font=(Configuracion.FUENTE_FAMILIA, 12, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        if top_data is not None:
            fig, ax = plt.subplots(figsize=(3, 2), dpi=100)
            self.figura_actual = fig  # Guardar referencia para exportar

            fig.patch.set_facecolor(Configuracion.COLOR_TARJETA)
            ax.set_facecolor(Configuracion.COLOR_TARJETA)

            sns.barplot(
                x=top_data.values,
                y=top_data.index,
                ax=ax,
                hue=top_data.index,
                legend=False,
                palette="Blues_r",
                edgecolor="none",
            )

            # Estilizado limpio
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["bottom"].set_color("#cbd5e1")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            ax.set_xlabel(
                "Viajes", color=Configuracion.COLOR_TEXTO_SECUNDARIO, fontsize=8
            )
            ax.set_ylabel("", color=Configuracion.COLOR_TEXTO_SECUNDARIO)
            ax.tick_params(
                axis="x", colors=Configuracion.COLOR_TEXTO_SECUNDARIO, labelsize=8
            )
            ax.tick_params(
                axis="y", colors=Configuracion.COLOR_TEXTO_PRINCIPAL, labelsize=8
            )

            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def _renderizar_kpis_top(self, parent, totales, kpis):
        """Renderiza la cuadrícula de KPIs numéricos en el cuadrante superior derecho."""
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 0))

        # Grid interno 3x2
        grid_kpis = ttk.Frame(frame, style="Panel.TFrame")
        grid_kpis.pack(fill="x")
        grid_kpis.columnconfigure(0, weight=1)
        grid_kpis.columnconfigure(1, weight=1)

        metricas = [
            (0, 0, "Viajes Totales", str(totales["viajes"])),
            (0, 1, "Coste Total", f"${totales['coste']:,.0f}"),
            (1, 0, "Distancia Media", f"{kpis['distancia_media']:.2f} km"),
            (1, 1, "Velocidad Media", f"{kpis['velocidad_media']:.1f} km/h"),
            (2, 0, "Coste / Km", f"${kpis['coste_km']:.2f}"),
            (2, 1, "Coste / Min", f"${kpis['coste_min']:.2f}"),
        ]

        for row, col, lbl, val in metricas:
            self._crear_kpi_grid(grid_kpis, row, col, lbl, val)

    def _renderizar_panel_inferior(self, parent, kpis, pago, desglose):
        """Renderiza las métricas de pago/pax y la tabla de desglose."""

        # --- A. Métricas Extra (Cuadrante Inferior Izq) ---
        frame_extra = ttk.Frame(parent, style="Panel.TFrame")
        frame_extra.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        frame_extra.columnconfigure(0, weight=1)  # Columna Pago
        frame_extra.columnconfigure(1, weight=1)  # Columna Pax

        # 1. Pago
        sub_pago = ttk.Frame(frame_extra, style="Panel.TFrame")
        sub_pago.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        ttk.Label(sub_pago, text="Pref. Pago", style="KPI.Label.TLabel").pack(
            anchor="w"
        )
        top_pago = pago.get("top_nombre", "N/A")
        ttk.Label(
            sub_pago,
            text=top_pago,
            style="KPI.Value.TLabel",
            foreground=Configuracion.COLOR_PRIMARIO,
            font=(Configuracion.FUENTE_FAMILIA, 14, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        for k, v in [
            ("Bizum", pago.get("bizum_pct", 0)),
            ("Efectivo", pago.get("efectivo_pct", 0)),
            ("Otros", pago.get("otros_pct", 0)),
        ]:
            ttk.Label(
                sub_pago,
                text=f"{k}: {v:.0f}%",
                style="Secundario.TLabel",
                font=(Configuracion.FUENTE_FAMILIA, 9),
            ).pack(anchor="w")

        # 2. Pasajeros
        sub_pax = ttk.Frame(frame_extra, style="Panel.TFrame")
        sub_pax.grid(row=0, column=1, sticky="nw")

        ttk.Label(sub_pax, text="Pax / Viaje", style="KPI.Label.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            sub_pax,
            text=f"{kpis['pax_medio']:.1f}",
            style="KPI.Value.TLabel",
            font=(Configuracion.FUENTE_FAMILIA, 24, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        # --- B. Tabla Desglose (Cuadrante Inferior Der) ---
        frame_tabla = ttk.Frame(parent, style="Panel.TFrame")
        frame_tabla.grid(row=1, column=1, sticky="nsew", padx=(0, 0))

        ttk.Label(
            frame_tabla,
            text="Desglose Costes",
            style="TituloPanel.TLabel",
            font=(Configuracion.FUENTE_FAMILIA, 11, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        cols = ("Concepto", "Promedio", "Porcentaje")
        tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=6)

        tabla.heading("Concepto", text="Concepto", anchor="w")
        tabla.heading("Promedio", text="Promedio ($)", anchor="e")
        tabla.heading("Porcentaje", text="% Total", anchor="e")

        tabla.column("Concepto", width=120, anchor="w")
        tabla.column("Promedio", width=80, anchor="e")
        tabla.column("Porcentaje", width=60, anchor="e")

        tabla.pack(fill="x", expand=True)

        for item in desglose["filas"]:
            tabla.insert(
                "",
                "end",
                values=(
                    item["concepto"],
                    f"${item['promedio']:.2f}",
                    f"{item['porcentaje']:.1f}%",
                ),
            )

        prom_total = desglose["total_promedio"]
        tabla.insert(
            "", "end", values=("TOTAL", f"${prom_total:.2f}", "100.0%"), tags=("total",)
        )
        tabla.tag_configure("total", font=(Configuracion.FUENTE_FAMILIA, 10, "bold"))

    def _renderizar_footer(self, parent, ultimo_registro):
        """Muestra el pie de página con información del último registro."""
        if ultimo_registro:
            ttk.Separator(parent, orient="horizontal").grid(
                row=3, column=0, columnspan=2, sticky="ew", pady=(20, 10)
            )
            info = f"Ultimo registro: {ultimo_registro.get('Hora_inicio')}"
            ttk.Label(parent, text=info, style="Secundario.TLabel").grid(
                row=4, column=0, columnspan=2, sticky="w"
            )

    def _crear_kpi_grid(self, parent, row, col, label, value):
        """Helper para crear una celda de KPI en un grid."""
        f = ttk.Frame(parent, style="Panel.TFrame")
        f.grid(row=row, column=col, sticky="w", pady=10, padx=5)
        ttk.Label(f, text=label, style="KPI.Label.TLabel").pack(anchor="w")
        ttk.Label(f, text=value, style="KPI.Value.TLabel").pack(anchor="w")
