import math
import tkinter as tk
from tkinter import messagebox
from controller.bar_properties import BarProperties
from controller.shear_calc import ShearCalculator
class BeamCalculator:
    def __init__(self, L, t, h, b, fc, fy, cargas_muertas, carga_viva):
        self.L = L          # Luz de la viga (m)
        self.t = t          # Tiempo en años
        self.h = h          # Altura de la viga (m)
        self.b = b          # Ancho de la viga (m)
        self.fc = fc        # Resistencia del concreto (MPa)
        self.fy = fy        # Resistencia del acero (MPa)
        self.cargas_muertas = cargas_muertas  # Cargas muertas adicionales (kN/m)
        self.carga_viva = carga_viva          # Carga viva (kN/m)
        # Variables para resultados
        self.As_requerida = None
        self.As_compresion = None
        self.mensaje_flexion = None
        self.resultados_cortante = None
        self.h_minima = None
        self.carga_muerta_total = None
        self.carga_total = None
        self.carga_ultima_mayorada = None
        self.Mu = None

    def diseño_flexion(self):
        """Realiza todos los cálculos de diseño por flexión"""
        try:
            dp=0.06
            # 1. Cálculo de la altura mínima
            self.h_minima = self.L / 16
            hmin_cm = self.h_minima * 100
            hmin_real = math.ceil(hmin_cm / 5) * 5
            
            # 2. Cálculo de cargas
            peso_propio = self.b * self.h * 24  # Densidad del concreto aprox. 24 kN/m³
            self.carga_muerta_total = peso_propio + self.cargas_muertas
            self.carga_total = self.carga_muerta_total + self.carga_viva
            self.carga_ultima_mayorada = 1.2 * self.carga_muerta_total + 1.6 * self.carga_viva

            # 3. Momento flector máximo
            self.Mu = (self.carga_ultima_mayorada * self.L**2) / 8  # Momento máximo en kN·m

            # Parámetros de diseño
            phi = 0.9  # Factor de resistencia
            Es = 200  # Módulo de elasticidad del acero (MPa)
            d = self.h - dp  # Brazo interno (m)
             # Brazo interno en metros

        # Determinar beta_1 según el valor de fc
            if self.fc <= 28:
                beta_1 = 0.85
            elif self.fc >= 55:
                beta_1 = 0.65
            else:
                beta_1 = 0.85 - ((0.05 * (self.fc - 28)) / 7)

            gamma = 0.85
            epsilon_u = 0.003
            rho_max = gamma * beta_1 * self.fc / self.fy * epsilon_u / (epsilon_u + 0.005)
            As_max = rho_max * self.b * d
            phi_M_max = phi * As_max * self.fy * (d - As_max * self.fy / (2 * gamma * self.fc * self.b))

            # Acero mínimo
            As_min1 = (self.fc**(0.5) * self.b * d) / (4 * self.fy)
            As_min2 = ((1.4 * self.b * d) / self.fy)
            As_min = max(As_min1, As_min2)

            Mu_MNm = self.Mu / 1000  # Convertir a MN·m

            # Cálculo de cantidad de acero
            if Mu_MNm < phi_M_max:
                num = phi * d - ((0.81 * d**2) - ((1.8 * Mu_MNm) / (gamma * self.fc * self.b)))**0.5
                den = (0.9 * self.fy) / (gamma * self.fc * self.b)
                As0 = num / den
                As = max(As0, As_min)
                As_mm = As * (10**6)
                Asp_mm = 0
                mensaje = "La viga no necesita acero a compresión."
            else:
                M2 = (Mu_MNm - phi_M_max) / 0.9
                Asp = M2 / (self.fy * (d - dp))  # dp = 0.06 m
                As = As_max + Asp
                As_mm = As * (10**6) + 337.65
                Asp_mm = Asp * (10**6)

                roY = gamma * self.fc / self.fy * beta_1 * epsilon_u / (epsilon_u - self.fy / Es) * dp / d + Asp / (self.b * d)
                ro = As / (self.b * d)

                if ro > roY:
                    mensaje = "La viga necesita acero a compresión. As' fluye"
                else:
                    a = (As - Asp) * self.fy / (gamma * self.fc * self.b)
                    c = a / beta_1
                    fsp = epsilon_u * Es * (c - 0.06) / c
                    AsRev = Asp * self.fy / fsp
                    mensaje = "La viga necesita acero a compresión. As' No fluye"

            self.As_requerida = As_mm+ 337.65
            self.As_compresion = Asp_mm
            self.mensaje_flexion = mensaje

            return {
                'h_minima': hmin_real,
                'altura_ok': self.h >= self.h_minima,
                'carga_muerta': self.carga_muerta_total,
                'carga_viva': self.carga_viva,
                'carga_total': self.carga_total,
                'carga_ultima': self.carga_ultima_mayorada,
                'momento_max': self.Mu,
                'as_requerida': As_mm,
                'as_compresion': Asp_mm,
                'mensaje': mensaje,
                'h': self.h
            }

        except Exception as e:
            raise ValueError(f"Error en cálculo de flexión: {str(e)}")


    def get_resultados_completos(self):
        """Devuelve todos los resultados calculados"""
        if not hasattr(self, 'Mu'):
            self.diseño_flexion()
        if not hasattr(self, 'resultados_cortante'):
            self.diseño_cortante()

        return {
            'flexion': {
                'as_requerida': self.As_requerida+337.65,
                'as_compresion': self.As_compresion,
                'mensaje': self.mensaje_flexion,
                'momento_max': self.Mu
            },
            'cortante': self.resultados_cortante,
            'geometria': {
                'h_minima': self.h_minima*100,
                'h_actual': self.h,
                'b': self.b,
                'L': self.L
            },
            'cargas': {
                'muerta': self.carga_muerta_total,
                'viva': self.carga_viva,
                'total': self.carga_total,
                'ultima': self.carga_ultima_mayorada
            }
        }