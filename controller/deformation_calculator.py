# controller/deformation_calc.py
import math
from tkinter import messagebox

class DeformationCalculator:
    def __init__(self, b, h, fc, L, carga_muerta, carga_viva, peso_propio, as_colocado, t):
        # Validaciones
        if None in [b, h, fc, L, carga_muerta, carga_viva, peso_propio, as_colocado, t]:
            raise ValueError("Todos los parámetros son obligatorios")
        
        # Entradas
        self.b = float(b)
        self.h = float(h)
        self.fc = float(fc)
        self.L = float(L)
        self.carga_muerta = float(carga_muerta)
        self.carga_viva = float(carga_viva)
        self.peso_propio = float(peso_propio)
        self.as_colocado = float(as_colocado)
        self.t = float(t)  # tiempo en años

        # Constantes y derivadas
        self.d = self.h - 0.06  # Peralte efectivo
        self.Ig = (self.b * self.h**3) / 12
        self.fr = 0.62 * (self.fc ** 0.5)
        self.yt = self.h / 2
        self.Mcr = (self.fr * self.Ig) / self.yt * 1000  # N·mm
        self.Ec = 3900 * (self.fc ** 0.5)  # MPa
        self.n = 200000 / self.Ec  # módulo de elasticidad acero/concreto

    def calcular(self):
        try:
            # Coeficientes cuadráticos para hallar c
            A = self.b * 1000 / 2
            B = self.n * self.as_colocado
            C = -self.n * self.as_colocado * self.d * 1000

            discriminante = B**2 - 4 * A * C
            if discriminante < 0:
                raise ValueError("La ecuación no tiene soluciones reales para c")

            c1 = (-B + math.sqrt(discriminante)) / (2 * A)
            c2 = (-B - math.sqrt(discriminante)) / (2 * A)
            c = max(c1, c2)

            # Inercia en estado agrietado
            Icr = (1/3) * (self.b * 1000) * c**3 + self.n * self.as_colocado * ((self.d * 1000) - c)**2

            carga_total = self.carga_muerta + self.carga_viva + self.peso_propio
            Ma1 = (carga_total * self.L**2) / 8
            Ma2 = ((self.carga_muerta + self.peso_propio) * self.L**2) / 8

            Ie1 = ((self.Mcr / Ma1)**3) * self.Ig + (1 - (self.Mcr / Ma1)**3) * Icr if Ma1 > 0 else None
            Ie2 = ((self.Mcr / Ma2)**3) * self.Ig + (1 - (self.Mcr / Ma2)**3) * Icr if Ma2 > 0 else None

            # Determinar ξ según el tiempo
            meses = self.t * 12
            if meses >= 60:
                xita = 2.0
            elif meses >= 12:
                xita = 1.4
            elif meses >= 6:
                xita = 1.2
            elif meses >= 3:
                xita = 1.0
            else:
                raise ValueError("El periodo debe ser al menos de 3 meses.")

            # Deformaciones
            L_mm = self.L * 1000
            delta_LD = (5 * carga_total * L_mm**4) / (384 * self.Ec * Ie2)
            delta_D = (5 * (self.carga_muerta + self.peso_propio) * L_mm**4) / (384 * self.Ec * Ie2)
            delta_L = delta_LD - delta_D
            delta_t = delta_L + xita * delta_D
            resultados={
                "Ig": self.Ig,
                "fr": self.fr,
                "Mcr": self.Mcr,
                "Ec": self.Ec,
                "n": self.n,
                "c": c,
                "Icr": Icr,
                "Ie1": Ie1,
                "Ie2": Ie2,
                "xita": xita,
                "delta_LD": delta_LD,
                "delta_D": delta_D,
                "delta_L": delta_L,
                "delta_t": delta_t,
                "Ma1": Ma1,
                "Ie1":Ie1,
                "Ma2":Ma2,
                "Ie2":Ie2
            }
            return resultados
        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            return None
