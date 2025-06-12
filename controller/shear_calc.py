# controller/shear_calc.py
import math

class ShearCalculator:
    def __init__(self, L, b, d, fc, carga_total, phi_v, fyv, cargas_muertas, carga_viva,h):
        # Validar tipos
        if None in [L, b, d, fc, cargas_muertas, carga_viva]:
            raise ValueError("Parámetros no pueden ser None")
        self.L = float(L)
        self.b = float(b)
        self.d = float(d)
        self.fc = float(fc)
        self.cargas_muertas = float(cargas_muertas)
        self.carga_viva = float(carga_viva)
        self.phi_v = 0.75
        self.fyv = float(fyv if fyv is not None else 420)  # Valor por defecto 420 MPas
        self.h = float(h)

    def calcular_cortante(self):
        # 2. Cálculo de cargas
        peso_propio = self.b * self.h * 24  # Densidad del concreto aprox. 24 kN/m³
        self.carga_muerta_total = peso_propio + self.cargas_muertas
        self.carga_total = self.carga_muerta_total + self.carga_viva
        self.carga_ultima_mayorada = 1.2 * self.carga_muerta_total + 1.6 * self.carga_viva
        wu = self.carga_ultima_mayorada  # Carga distribuida en kN/m
        V_max = (wu * self.L) / 2  # Cortante máximo en kN
        Vc = 0.75 * (0.17 * math.sqrt(self.fc) * self.b * self.d) * 1000  # Resistencia al cortante del concreto en kN
        Vud = wu * ((self.L / 2) - self.d)
        # Límites de cortante
        Vmax1 = 0.66 * (math.sqrt(self.fc) * self.b * self.d) * 1000 
        Vmax2 = 0.33 * (math.sqrt(self.fc) * self.b * self.d) * 1000 
        phiVc = 0.75 * Vc
        Vmin = 0.75 * (Vc / 2)
        # Propiedades de estribos (#3)
        As_e = 71  # mm²
        Av = As_e * 2
        Vs = max((Vud - phiVc) / self.phi_v, 0)
        d_cm = self.d * 100
    
        resultados = {
            "V_max": V_max,
            "Vc": Vc,
            "Vud": Vud,
            "phiVc": phiVc,
            "Vmin": Vmin,
            "xinicio": 0,
            "xfinal": 0,
            "sE": 0,
            "Vx": 0,
            "separaciones": []
        }
    
        xi = self.L / 8
        x_eval = [xi * i for i in range(5)]
    
        for x in x_eval:
            Vx = -wu * x + (wu * self.L) / 2
            sE = 0  # Valor por defecto

            if Vx > Vmin:
                # Calcular separación requerida
                if Vs > 0:
                    S1 = (Av * self.fyv * self.d) / (Vs * 10)  # en cm
                    S1 = math.floor(S1)
                else:
                    S1 = float('inf')

                # Calcular separación máxima permitida
                if Vx > Vmax2:
                    if Vx <= Vmax1:
                        Smax1 = d_cm / 4
                        Smax2 = 30  # cm
                        S2 = min(Smax1, Smax2)
                    else:
                        Smax1 = d_cm / 2
                        Smax2 = 60  # cm
                        S2 = min(Smax1, Smax2)
                    S2 = math.floor(S2)
                    sE = min(S1, S2) if S1 != float('inf') else S2
                else:
                    # Refuerzo mínimo
                    Smin = (self.fyv * Av) / (0.062 * math.sqrt(self.fc) * (self.b * 1000))  # mm
                    sE = math.floor(Smin / 10)  # cm

            # Determinar rango del tramo
            if x == 0:
                xinicio = 0
                xfinal = xi
            else:
                xinicio = x
                xfinal = x + xi if x + xi <= self.L/2 else self.L/2

            # Guardar resultados del tramo
            resultados["separaciones"].append({
                "xinicio": xinicio,
                "xfinal": xfinal,
                "sE": sE,
                "Vx": Vx
            })

        # También guardar los primeros valores en el diccionario principal
        if resultados["separaciones"]:
            primeros_resultados = resultados["separaciones"][0]
            resultados.update({
                "xinicio": primeros_resultados["xinicio"],
                "xfinal": primeros_resultados["xfinal"],
                "sE": primeros_resultados["sE"],
                "Vx": primeros_resultados["Vx"]
            })

        return resultados
