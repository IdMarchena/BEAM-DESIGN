import tkinter as tk
from tkinter import messagebox
import math
from controller.bar_properties import BarProperties

class BarSelectionWindow(tk.Toplevel):
    def __init__(self, parent, as_required, callback_guardar,b):
        super().__init__(parent)
        self.title("Selección de Barras")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.as_required = as_required
        self.callback_guardar = callback_guardar
        self.bar_props = BarProperties()
        self.b=b
        self.diametro = None
        self.as_colocado = None
        self.area_barra = None
        self.nro_barra = None
        self.sep_barras = None

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text=f"Área de acero requerida: {self.as_required:.2f} mm²").pack(pady=10)

        tk.Label(self, text="Ingresa el número de la barra:").pack(pady=5)
        self.entry_barra = tk.Entry(self)
        self.entry_barra.pack()

        self.btn_calcular = tk.Button(self, text="Calcular barras", command=self.calcular_barras)
        self.btn_calcular.pack(pady=10)

        self.label_resultado = tk.Label(self, text="", justify=tk.LEFT)
        self.label_resultado.pack(pady=10)

        self.btn_usar = tk.Button(self, text="Usar estos valores", command=self.guardar)
        self.btn_usar.pack(pady=10)
        self.btn_usar.config(state=tk.DISABLED)

    def calcular_barras(self):
        try:
            nro = self.entry_barra.get().strip()
            propiedades = self.bar_props.get_bar(nro)

            if propiedades is None:
                raise ValueError("La barra ingresada no existe.")

            self.nro_barra = nro
            self.diametro = propiedades['diametro']
            self.area_barra = propiedades['area']

            cantidad_barras = math.ceil(self.as_required / self.area_barra)
            self.as_colocado = cantidad_barras * self.area_barra
            #Espaceamiento
            self.sep_barras = (((self.b * 1000) - (2 * 40) -(2*9.5) - (cantidad_barras * self.diametro))-(cantidad_barras*self.diametro)) / (cantidad_barras - 1)

            self.label_resultado.config(text=(
                f"Diámetro: {self.diametro} mm\n"
                f"Área barra: {self.area_barra:.2f} mm²\n"
                f"Cantidad: {cantidad_barras}\n"
                f"As colocado: {self.as_colocado:.2f} mm²\n"
                f"Espaciamiento (S): {self.sep_barras:.2f} mm\n"
                f"Número de barra seleccionada: {nro}"
            ))

            self.btn_usar.config(state=tk.NORMAL)

            # ← Mueve la creación del diccionario aquí, después de definir todas las variables
            resultados = {
                "diametro": self.diametro,
                "area_barra": self.area_barra,
                "cantidad_barras": cantidad_barras,
                "as_colocado": self.as_colocado,
                "sep_barras": self.sep_barras ,  
                "nro_barra": nro
            }

            return resultados

        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            self.btn_usar.config(state=tk.DISABLED)
            return None

    def guardar(self):
        if self.diametro and self.as_colocado and self.area_barra and self.nro_barra:
            self.callback_guardar(
            diametro=self.diametro,
            as_colocado=self.as_colocado,
            area_barra=self.area_barra,
            nro_barra=self.nro_barra,
            sep_barras=self.sep_barras  # ← Añade este parámetro
            )
            self.destroy()
        else:
            messagebox.showerror("Error", "Primero debes calcular correctamente.")
