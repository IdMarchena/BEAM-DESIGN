import tkinter as tk
from tkinter import messagebox
from controller.beam_calculator import BeamCalculator
from controller.beam_drawer import BeamDrawer
from view.bar_selection import BarSelectionWindow
from utilities.pdf_exporter import export_to_pdf
from model.beam_model import BeamModel
from controller.shear_calc import ShearCalculator
from controller.deformation_calculator import DeformationCalculator
from view.iteration_window import iterationWindow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diseño de Vigas SR")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        self.model = None
        self.calculator = None
        self.diametro_barra = None
        self.as_colocado = None
        self.area_barra = None
        self.nro_barra = None
        self.sep_barras=None
        self.resultados_globales = {}

        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        self.frame = tk.Frame(self)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        variables = [
            ("Luz de la viga (m):", "L"),
            ("Tiempo en años (t):", "t"),
            ("Altura de la viga (h, m):", "h"),
            ("Ancho de la viga (b, m):", "b"),
            ("Resistencia del concreto (f'c, MPa):", "fc"),
            ("Resistencia del acero (fy, MPa):", "fy"),
            ("Cargas muertas adicionales (kN/m):", "cargas_muertas"),
            ("Carga viva (kN/m):", "carga_viva"),
        ]
        self.entries = {}
        for i, (label_text, var_name) in enumerate(variables):
            tk.Label(self.frame, text=label_text).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(self.frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.entries[var_name] = entry

        # Botón para calcular
        self.btn_calcular = tk.Button(self.frame, text="Calcular", command=self.calcular)
        self.btn_calcular.grid(row=len(variables), column=0, columnspan=2, pady=10)

        # Área de texto para resultados
        self.text_resultados = tk.Text(self, height=20, width=80)
        self.text_resultados.pack(padx=10, pady=10)
        self.text_resultados.tag_config("negrilla", font=("Helvetica", 10, "bold"))
        
        # Frame para centrar los botones inferiores
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.grid(row=len(variables)+1, column=0, columnspan=2, pady=10)
        
        # Botón para dibujar viga
        self.btn_dibujar = tk.Button(self.button_frame, text="Dibujar Viga", command=self.dibujar_desde_principal)
        self.btn_dibujar.pack(side=tk.LEFT, padx=5)

        # Botón para diagrama de interacción
        self.btn_diagrama_interaccion = tk.Button(self.button_frame, 
                                                text="Diagrama de Interacción", 
                                                command=self.abrir_diagrama_interaccion)
        self.btn_diagrama_interaccion.pack(side=tk.LEFT, padx=5)

        # Botón para exportar PDF
        self.btn_exportar = tk.Button(self.button_frame, 
                                    text="Guardar como PDF",
                                    command=lambda: export_to_pdf(self.text_resultados.get("1.0", tk.END)))
        self.btn_exportar.pack(side=tk.LEFT, padx=5)


    def setup_layout(self):
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=3)
        self.frame.grid_rowconfigure(8, weight=1)

    def calcular(self):
        try:
            print("[INFO] Iniciando cálculo...")
            inputs = {
                'L': float(self.entries['L'].get()),
                't': float(self.entries['t'].get()),
                'h': float(self.entries['h'].get()),
                'b': float(self.entries['b'].get()),
                'fc': float(self.entries['fc'].get()),
                'fy': float(self.entries['fy'].get()),
                'cargas_muertas': float(self.entries['cargas_muertas'].get()),
                'carga_viva': float(self.entries['carga_viva'].get())
            }
            print("[INFO] Creando instancia del modelo" )
            self.model = BeamModel()
            for key, value in inputs.items():
                setattr(self.model, key, value)
            print("[INFO] Calculando variables auxiliares" )
            self.model.calcular_variables_auxiliares()

            required_vars = ['L', 'b', 'd', 'fc', 'fy', 'fyv', 'carga_ultima_mayorada']
            for var in required_vars:
                if getattr(self.model, var) is None:
                    raise ValueError(f"La variable {var} no fue calculada correctamente")
            print("[INFO] Creando instancia del la clase que hace los calculos para la viga" )
            self.calculator = BeamCalculator(
                L=self.model.L, t=self.model.t, h=self.model.h, b=self.model.b,
                fc=self.model.fc, fy=self.model.fy,
                cargas_muertas=self.model.cargas_muertas, carga_viva=self.model.carga_viva
            )
            print("[INFO] retornado la lista de variables instancia del modelo" )
            resultados_flexion = self.calculator.diseño_flexion()
            print("[INFO] Creando instancia del la clase que hace los calculos para cortante de la viga" )
            self.shearCalculator = ShearCalculator(
                L=self.model.L, b=self.model.b, d=self.model.d,
                fc=self.model.fc, carga_total=self.model.carga_total,
                phi_v=self.model.phi_v, fyv=self.model.fyv,
                carga_ultima_mayorada=self.model.carga_ultima_mayorada
            )
            print("[INFO] retornado la lista de variables instancia del modelo" )
            resultados_cortante = self.shearCalculator.calcular_cortante()


            print("[INFO] uniendo as 3 listas de resultado en una lista global de variables" )
            self.resultados_globales = {**resultados_flexion, **resultados_cortante}


            print("[INFO] abriendo la ventana extra para el calculo de los espaceamientos" )
            # Abre ventana para seleccionar barras
            BarSelectionWindow(
                parent=self,
                as_required=self.resultados_globales['as_requerida'],
                callback_guardar=self.update_bar_data,
                b=self.model.b
            )


        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def update_bar_data(self, diametro, as_colocado, area_barra, nro_barra, sep_barras):
        self.diametro_barra = diametro
        self.as_colocado = as_colocado
        self.area_barra = area_barra
        self.nro_barra = nro_barra
        self.sep_barras = sep_barras  
        self.model.as_colocado=as_colocado
        
        # Agrega datos a resultados globales

        self.resultados_globales.update({
        'diametro': diametro,
        'as_colocado': as_colocado,
        'area_barra': area_barra,
        'nro_barra': nro_barra,
        'cantidad_barras': as_colocado / area_barra if area_barra else 0,
        'sep_barras': sep_barras  
        })


        print("[INFO] Creando instancia del la clase que hace los calculos para las deformaciones de la viga") 
        self.deformationCalculator = DeformationCalculator(
        b=self.model.b,
        h=self.model.h,
        fc=self.model.fc,
        L=self.model.L,
        carga_muerta=self.model.cargas_muertas,
        carga_viva=self.model.carga_viva,
        peso_propio=self.model.b * self.model.h * 24,
        as_colocado=self.as_colocado,
        t=float(self.entries['t'].get())
        )

        print("[INFO] retornado la lista de variables instancia de las deformaciones")
        resultados_deformaciones = self.deformationCalculator.calcular()

        if resultados_deformaciones:
            self.resultados_globales.update(resultados_deformaciones)

        print("[INFO] retornado la lista de variables instancia de las deformaciones")
        self.mostrar_resultados(self.resultados_globales)


    def mostrar_resultados(self, resultados):
        self.text_resultados.delete('1.0', tk.END)
        self.text_resultados.insert(tk.END, "=== RESULTADOS DEL CÁLCULO ===\n\n", "negrilla")

        # Geometría
        self.text_resultados.insert(tk.END, "--- Geometría ---\n")
        self.text_resultados.insert(tk.END, f"Altura mínima recomendada: {resultados['h_minima']:.2f} m\n")
        self.text_resultados.insert(tk.END, f"Advertencia para la altura: {'✅ OK' if resultados['h'] > resultados['h_minima'] else '⚠️ Menor al mínimo'} ({self.model.h} m)\n\n")

        # Cargas
        self.text_resultados.insert(tk.END, "--- Cargas ---\n", "negrilla")
        self.text_resultados.insert(tk.END, f"Carga muerta total (D): {resultados['carga_muerta']:.2f} kN/m\n")
        self.text_resultados.insert(tk.END, f"Carga viva (L): {resultados['carga_viva']:.2f} kN/m\n")
        self.text_resultados.insert(tk.END, f"Carga última mayorada: {resultados['carga_ultima']:.2f} kN/m\n\n")

        # Flexión
        self.text_resultados.insert(tk.END, "--- Flexión ---\n", "negrilla")
        self.text_resultados.insert(tk.END, f"Momento máximo (Mu): {resultados['momento_max']:.2f} kN·m\n")
        self.text_resultados.insert(tk.END, f"As requerida: {resultados['as_requerida']:.2f} mm²\n")
        if resultados['as_compresion'] > 0:
            self.text_resultados.insert(tk.END, f"As' (compresión): {resultados['as_compresion']:.2f} mm²\n")
        self.text_resultados.insert(tk.END, f"Estado: {resultados['mensaje']}\n\n")

        # Cortante
        self.text_resultados.insert(tk.END, "--- Cortante ---\n", "negrilla")
        self.text_resultados.insert(tk.END, f"Cortante máximo (Vmax): {resultados['V_max']:.2f} kN\n")
        self.text_resultados.insert(tk.END, f"Vc (concreto): {resultados['Vc']:.2f} kN\n")
        self.text_resultados.insert(tk.END, f"Vud: {resultados['Vud']:.2f} kN\n")
        self.text_resultados.insert(tk.END, f"phiVc: {resultados['phiVc']:.2f} kN\n")
        self.text_resultados.insert(tk.END, f"phiVc/2: {resultados['Vmin']:.2f} kN\n\n")
        
        #Espaciamiento
        self.text_resultados.insert(tk.END, f"Espaciamiento entre los estribos = {resultados['sE']:.2f} cm desde {resultados['xinicio']:.2f} m hasta {resultados['xfinal']:.2f} m\n")
        # Mostrar todos los tramos
        for tramo in resultados.get("separaciones", []):
            if tramo['sE'] > 0:
                self.text_resultados.insert(tk.END, 
                    f"Tramo {tramo['xinicio']:.2f}-{tramo['xfinal']:.2f}m: "
                    f"Estribos @ {tramo['sE']:.2f}cm (Vx={tramo['Vx']:.2f}kN)\n")
            else:
                self.text_resultados.insert(tk.END, 
                    f"Tramo {tramo['xinicio']:.2f}-{tramo['xfinal']:.2f}m: "
                    "No se requieren estribos\n")
        print("[INFO] Imprimiendo los resultados de espaceamiento que son", resultados['xinicio'])


        # Verificación de espaciamiento mínimo
        if (resultados['nro_barra'] in {"8", "9", "10", "11", "14", "18"} and resultados['sE'] < 25.4) or \
           (resultados['nro_barra'] not in {"8", "9", "10", "11", "14", "18"} and resultados['sE'] < resultados['diametro']):
            self.text_resultados.insert(tk.END, "⚠️ El espaciamiento calculado no cumple con los requisitos mínimos.\n")
        print("[INFO] Imprimiendo los resultados de Barras que son")
        # Barras
        self.text_resultados.insert(tk.END, "--- Barras ---\n", "negrilla")
        self.text_resultados.insert(tk.END, f"Número de barra: #{resultados['nro_barra']}\n")
        self.text_resultados.insert(tk.END, f"Diámetro: {resultados['diametro']:.2f} mm\n")
        self.text_resultados.insert(tk.END, f"Área de una barra: {resultados['area_barra']:.2f} mm²\n")
        self.text_resultados.insert(tk.END, f"Cantidad: {resultados['cantidad_barras']:.0f}\n")
        self.text_resultados.insert(tk.END, f"As colocado: {resultados['as_colocado']:.2f} mm²\n")
        self.text_resultados.insert(tk.END, f"Espaciamiento entre barras: {resultados.get('sep_barras', 0):.2f} mm\n")
        self.btn_dibujar['state'] = tk.NORMAL
        self.btn_exportar['state'] = tk.NORMAL

        #analisis de viga
        print("[INFO] Imprimiendo los resultados de las deformaciones que son", resultados['Ig'])
        self.text_resultados.insert(tk.END, "--- Comportamiento de la viga ---\n", "negrilla")
        self.text_resultados.insert(tk.END, f"Inercia sin agrietar (Ig): {resultados['Ig']:.5f} m⁴\n")
        self.text_resultados.insert(tk.END, f"Momento de agrietamiento (Mcr): {resultados['Mcr']:.5f} kN·m\n")
        self.text_resultados.insert(tk.END, f"Módulo de elasticidad del concreto (Ec): {resultados['Ec']:.2f} MPa\n")
        self.text_resultados.insert(tk.END, f"Razón modular (n): {resultados['n']:.5f}\n")
        self.text_resultados.insert(tk.END, f"Distancia c: {resultados['c']:.2f} mm\n")
        self.text_resultados.insert(tk.END, f"Inercia agrietada (Icr): {resultados['Icr']:.2f} mm⁴\n")

        self.text_resultados.insert(tk.END, f"Momento actuante Ma1 (carga muerta + carga viva): {resultados['Ma1']:.2f} kN·m\n")
        self.text_resultados.insert(tk.END, f"Inercia efectiva Ie1: {resultados['Ie1']:.2f} mm⁴\n")
        self.text_resultados.insert(tk.END, f"Momento actuante Ma2 (solo carga muerta): {resultados['Ma2']:.2f} kN·m\n")
        self.text_resultados.insert(tk.END, f"Inercia efectiva Ie2: {resultados['Ie2']:.2f} mm⁴\n")
        self.text_resultados.insert(tk.END, f"-------------------------------\n")
        #Deformaciones
        print("[INFO] Imprimiendo los resultados de las deformaciones que son", resultados['delta_LD'])
        self.text_resultados.insert(tk.END, f"\n--- Deformaciones Calculadas ---\n")
        self.text_resultados.insert(tk.END, f"Deformación Δ(L+D): {resultados['delta_LD']:.5f} mm\n")
        self.text_resultados.insert(tk.END, f"Deformación Δ(D): {resultados['delta_D']:.5f} mm\n")
        self.text_resultados.insert(tk.END, f"Deformación Δ(L): {resultados['delta_L']:.5f} mm\n")
        self.text_resultados.insert(tk.END, f"Deformación Δ(t): {resultados['delta_t']:.5f} mm\n")
        self.text_resultados.insert(tk.END, f"-------------------------------\n")

    def abrir_diagrama_interaccion(self):
        ventana_diagrama = iterationWindow()
        ventana_diagrama.mainloop()

    def dibujar_desde_principal(self):
        if not all([self.diametro_barra, self.as_colocado, self.area_barra]):
            messagebox.showerror("Error", "Primero calcule y seleccione las barras")
            return
        try:
            b = float(self.entries['b'].get()) * 1000
            h = float(self.entries['h'].get()) * 1000
            drawer = BeamDrawer(b, h, 40, self.diametro_barra, self.as_colocado, self.area_barra)
            drawer.draw()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo dibujar: {str(e)}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()