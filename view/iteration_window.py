import tkinter as tk
from tkinter import messagebox
from controller.iteration_calculator import Iteration_calculator

class iterationWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diagrama de iteración")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        self.calculator = None
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(padx=10, pady=10)

        variables = [
            ("Recubrimiento (cm):", "recubrimiento"),
            ("fc (kg/cm²):", "fc"),
            ("fy (kg/cm²):", "fy"),
            ("Base (cm):", "base"),
            ("Altura (cm):", "altura"),
            ("Nº aceros X:", "numero_aceros_x"),
            ("Nº aceros Y:", "numero_aceros_y"),
            ("Diámetro (ej. 1/2):", "diametro"),
            ("Carga Momento (ton·m):", "carga_momento"),
            ("Carga Compresión (ton):", "carga_compresion")
        ]

        for i, (label, key) in enumerate(variables):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky="e")
            entry = tk.Entry(frame)
            entry.grid(row=i, column=1)
            self.entries[key] = entry

        tk.Button(frame, text="Calcular y Mostrar Diagramas", command=self.calcular).grid(row=len(variables), column=0, columnspan=2, pady=10)

    def calcular(self):
        try:
            datos = {key: self.entries[key].get() for key in self.entries}
            self.calculator = Iteration_calculator(
                recubrimiento=float(datos['recubrimiento']),
                fc=float(datos['fc']),
                fy=float(datos['fy']),
                Es=2.0e6,
                base=float(datos['base']),
                altura=float(datos['altura']),
                numero_aceros_x=int(datos['numero_aceros_x']),
                numero_aceros_y=int(datos['numero_aceros_y']),
                diametro=datos['diametro'],
                carga_momento=float(datos['carga_momento']),
                carga_compresion=float(datos['carga_compresion']),
                etiqueta="Columna"
            )
            self.calculator.generar_graficas()
        except Exception as e:
            messagebox.showerror("Error", f"Error en el cálculo: {e}")

if __name__ == "__main__":
    app = iterationWindow()
    app.mainloop()
