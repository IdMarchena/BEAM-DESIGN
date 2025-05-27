import numpy as np
import matplotlib.pyplot as plt

class Iteration_calculator:
    def __init__(self, recubrimiento, fc, fy, Es, base, altura, numero_aceros_x, numero_aceros_y, diametro, carga_momento, carga_compresion, etiqueta="C12 Nivel 1"):
        self.recubrimiento = recubrimiento
        self.fc = fc
        self.fy = fy
        self.Es = Es
        self.base = base
        self.altura = altura
        self.numero_aceros_x = numero_aceros_x
        self.numero_aceros_y = numero_aceros_y
        self.diametro = diametro
        self.carga_momento = carga_momento
        self.carga_compresion = carga_compresion
        self.etiqueta = etiqueta
        self.beta1 = 0
        self.d_prima = recubrimiento
        self.peralte_efectivo = altura - recubrimiento
        self.altura_efectiva = altura - 2 * recubrimiento
        self.altura_espaciamiento = self.altura_efectiva / (numero_aceros_y - 1)
        self.Ag = base * altura
        self.numero_aceros = 2 * numero_aceros_x + 2 * numero_aceros_y - 4

        self.εc = 0.003
        self.εy = fy / Es

        self.distancias2 = [self.altura_espaciamiento * i + recubrimiento for i in range(numero_aceros_y)]
        self.As1 = self.obtener_area_acero()

        self.Areas_nn = []
        for i in range(numero_aceros_y):
            if i == 0 or i == (numero_aceros_y - 1):
                self.Areas_nn.append(self.As1 * numero_aceros_x)
            else:
                self.Areas_nn.append(self.As1 * 2.0)

        self.cuantia = sum(self.Areas_nn) / self.Ag
        # Beta 1 
        if self.fc < 280:
            self.beta1 = 0.85
        else:
            self.beta1 = max(0.85 - 0.05 * (self.fc - 280) / 7, 0.65)

        self.Ast = self.numero_aceros * self.As1
        self.pn = (0.85 * fc * (self.Ag - self.Ast) + self.Ast * self.fy)
        self.Pnmax = 0.8 * self.pn  # Para columnas con estribos
        # Φ=0.65 factor de minoracion para seccion controladas por compresion
        self.Pumax = 0.65 * self.Pnmax              
        self.PCPN = [0, self.Pnmax]
        self.PCPU = [0, self.Pumax]
        self.carga_nom_ACI = []
        self.carga_ult_ACI = []
        self.momento_nom_ACI = []
        self.momento_ult_ACI = []
        
    def obtener_area_acero(self):
        tabla = {
            "1/4": 0.32,
            "3/8": 0.71,
            "1/2": 1.27,
            "5/8": 1.98,
            "3/4": 2.84,
            "1": 5.10
        }
        return tabla.get(self.diametro, 0.0)

    def phi_ACI(self, εs):
        phi_factor = 0.65 + 0.25 * (εs - self.εy) / (0.005 - self.εy)
        if phi_factor >= 0.90:
            phi = 0.90        # Controlado por la Tension
        elif phi_factor <= 0.65:
            phi = 0.65        # Controlado por la Compresion
        else:
            phi = phi_factor  # Transicion
        return phi

    def phi_E060(self, Pn):
        phi = 0.65
        if Pn > 0.1 * self.Ag * self.fc:
            phi = 0.65
        elif Pn > 0:
            phi = 0.9 - 2 / (self.fc * self.Ag) * Pn
        else:
            phi = 0.9
        return phi

    def calcular_interaccion(self, c, phi_func):
        εsi = [(self.εc * abs(c - d) / c) for d in self.distancias2]
        fsi = [min(self.Es * ε, self.fy) for ε in εsi]
        Cc = [(self.Areas_nn[i] * fsi[i] if c > self.distancias2[i] or i == 0 else -self.Areas_nn[i] * fsi[i]) for i in range(self.numero_aceros_y)]
        BP = [(0.5 * self.altura - d if self.altura * 0.5 > d else d - 0.5 * self.altura) for d in self.distancias2]
        MP = [(-BP[i] * Cc[i] if self.distancias2[i] > 0.5 * self.altura or BP[i] * Cc[i] < 0 else BP[i] * Cc[i]) for i in range(self.numero_aceros_y)]

        F_concreto = 0.85 * self.fc * (0.85 * c) * self.base
        M_concreto = F_concreto * (self.altura * 0.5 - 0.85 * c * 0.5)

        Cc.append(F_concreto)
        MP.append(M_concreto)

        Pn = sum(Cc)
        Mn = sum(MP)
        phi = phi_func(εsi[-1]) if phi_func == self.phi_ACI else phi_func(Pn)
        return Pn, phi * Pn, Mn, phi * Mn

    def generar_graficas(self):
        valores_c = np.arange(self.altura + self.altura / 4, self.recubrimiento, -0.5)

        cargas_nom_aci, cargas_ult_aci, momentos_nom_aci, momentos_ult_aci = [], [], [], []
        cargas_nom_e060, cargas_ult_e060, momentos_nom_e060, momentos_ult_e060 = [], [], [], []
        P_T = -self.Ast * self.fy
        for c in valores_c:
            Pn, Pu, Mn, Mu = self.calcular_interaccion(c, self.phi_ACI)
            cargas_nom_aci.append(Pn)
            cargas_ult_aci.append(Pu)
            momentos_nom_aci.append(Mn)
            momentos_ult_aci.append(Mu)

        valores_c = np.arange(self.altura + self.altura / 4, self.recubrimiento, -0.5)

        for c in valores_c:
            Pn, Pu, Mn, Mu = self.calcular_interaccion(c, self.phi_E060)
            cargas_nom_e060.append(Pn)
            cargas_ult_e060.append(Pu)
            momentos_nom_e060.append(Mn)
            momentos_ult_e060.append(Mu)
            
            
        Mn_T = 0.00
        TP = [Mn_T, P_T]
        TPU = [0.9 * Mn_T, 0.9 * P_T]
        
        # Para el ploteo
        carga_nom_bal = []
        momento_nom_bal = []
        Cb = (6000.00 * self.peralte_efectivo) / (6000.00 + self.fy)
        Pn_bal, Pu_bal, Mn_bal, Mu_bal = self.calcular_interaccion(Cb, self.phi_ACI)
        
        # No importa que diagrama se utilice, la falla balanceada es la misma
        carga_nom_bal.append(Pn_bal)
        momento_nom_bal.append(Mn_bal)
        carga_nom_bal.append(0)
        momento_nom_bal.append(0)
        
        # Uniendo los puntos del diagrama y dando forma 
        carga_nom_r_ACI = list(cargas_nom_aci)
        carga_ult_r_ACI = list(cargas_ult_aci)
        momento_nom_r_ACI = list(momentos_nom_aci)
        momento_ult_r_ACI = list(momentos_ult_aci)
        
        for i in range(len(momentos_nom_aci)):
            if momentos_nom_aci[i] >= self.Pnmax:
                carga_nom_r_ACI[i] = self.Pnmax
        
        for i in range(len(cargas_ult_aci)):
            if cargas_ult_aci[i] >= self.Pumax:
                carga_ult_r_ACI[i] = self.Pumax 
                
        # Uniendo el punto de traccion pura  
        carga_nom_r_ACI.append(P_T)     
        momento_nom_r_ACI.append(0)
        carga_ult_r_ACI.append(0.9 * P_T)
        momento_ult_r_ACI.append(0) 
        
        # Uniendo los puntos del diagrama y dando forma 
        carga_nom_r_E060 = list(cargas_nom_e060)
        carga_ult_r_E060 = list(cargas_ult_e060)
        momento_nom_r_E060 = list(momentos_nom_e060)
        momento_ult_r_E060 = list(momentos_ult_e060)
        
        for i in range(len(cargas_nom_e060)):
            if cargas_nom_e060[i] >= self.Pnmax:
                carga_nom_r_E060[i] = self.Pnmax

        for i in range(len(cargas_ult_e060)):
            if cargas_ult_e060[i] >= self.Pumax:
                carga_ult_r_E060[i] = self.Pumax  
                
        # Uniendo el punto de traccion pura  
        carga_nom_r_E060.append(P_T)     
        momento_nom_r_E060.append(0)
        carga_ult_r_E060.append(0.9 * P_T)
        momento_ult_r_E060.append(0)

        self.mostrar_diagramas(
            momento_nom_bal, carga_nom_bal, 
            momentos_nom_aci, cargas_nom_aci, momento_nom_r_ACI, carga_nom_r_ACI,
            momentos_ult_aci, cargas_ult_aci, momento_ult_r_ACI, carga_ult_r_ACI,
            momentos_nom_e060, cargas_nom_e060, momento_nom_r_E060, carga_nom_r_E060,
            momentos_ult_e060, cargas_ult_e060, momento_ult_r_E060, carga_ult_r_E060
        )

    def mostrar_diagramas(self, momento_nom_bal, carga_nom_bal, 
                         momento_nom_ACI, carga_nom_ACI, momento_nom_r_ACI, carga_nom_r_ACI,
                         momento_ult_ACI, carga_ult_ACI, momento_ult_r_ACI, carga_ult_r_ACI,
                         momento_nom_E060, carga_nom_E060, momento_nom_r_E060, carga_nom_r_E060,
                         momento_ult_E060, carga_ult_E060, momento_ult_r_E060, carga_ult_r_E060):
        
        fig = plt.figure(figsize=(21, 10))
        
        # ACI
        ax1 = plt.subplot(1, 3, 1)
        ax1.plot(np.array(momento_nom_bal)/100000, np.array(carga_nom_bal)/1000, linestyle='--', color="black", linewidth=1, alpha=0.4)
        ax1.plot(np.array(momento_nom_ACI)/100000, np.array(carga_nom_ACI)/1000, linestyle='--', color="silver")
        C_N, = ax1.plot(np.array(momento_nom_r_ACI)/100000, np.array(carga_nom_r_ACI)/1000, linestyle='-', color="black")
        ax1.plot(np.array(momento_ult_ACI)/100000, np.array(carga_ult_ACI)/1000, linestyle='--', color="lightcoral")
        C_D, = ax1.plot(np.array(momento_ult_r_ACI)/100000, np.array(carga_ult_r_ACI)/1000, linestyle='-', color="red")

        ax1.plot(self.carga_momento, self.carga_compresion, "kx", ms=9)
        ax1.set_ylabel("P (ton)")
        ax1.set_xlabel("M (ton.m)")
        ax1.set_title("DIAGRAMA DE INTERACCION ACI 318-19", fontweight="bold")
        ax1.legend((C_N, C_D), ("Curva Nominal Teorica", "Curva Diseño ACI 318"), loc='upper right', shadow=True)
        ax1.grid(linewidth=0.6)
        ax1.set(xlim=(0))
        ax1.set_facecolor("white")

        # E060
        ax2 = plt.subplot(1, 3, 2)
        ax2.plot(np.array(momento_nom_bal)/100000, np.array(carga_nom_bal)/1000, linestyle='--', color="black", linewidth=1, alpha=0.4)
        ax2.plot(np.array(momento_nom_E060)/100000, np.array(carga_nom_E060)/1000, linestyle='--', color="silver")
        C_N, = ax2.plot(np.array(momento_nom_r_E060)/100000, np.array(carga_nom_r_E060)/1000, linestyle='-', color="black")
        ax2.plot(np.array(momento_ult_E060)/100000, np.array(carga_ult_E060)/1000, linestyle='--', color="lightcoral")
        C_D, = ax2.plot(np.array(momento_ult_r_E060)/100000, np.array(carga_ult_r_E060)/1000, linestyle='-', color="red")
        
        ax2.plot(self.carga_momento, self.carga_compresion, "kx", ms=9)
        ax2.set_ylabel("P (ton)")
        ax2.set_xlabel("M (ton.m)")
        ax2.set_title("DIAGRAMA DE INTERACCION E060", fontweight="bold")
        ax2.legend((C_N, C_D), ("Curva Nominal Teorica", "Curva Diseño E060"), loc='upper right', shadow=True)
        ax2.grid(linewidth=0.6)
        ax2.set(xlim=(0))
        ax2.set_facecolor("white")

        # SECCION
        b = self.base
        h = self.altura
        e = 4  # cm - recubrimiento
        rx = 1.2  # variable, hace referencias al diametro en el plot
        ry = 0.9
        rectangulo_x = [0, b, b, 0, 0]
        rectangulo_y = [0, 0, h, h, 0]
        estribo_x = [e, b-e, b-e, e, e]
        estribo_y = [e, e, h-e, h-e, e]
        k_x = self.numero_aceros_x - 1
        k_y = self.numero_aceros_y - 1
        s_x = (b - 2 * e - 2 * rx) / k_x
        s_y = (h - 2 * e - 2 * ry) / k_y
        
        varillas_x = []
        varillas_y = []
        for i in range(self.numero_aceros_x):
            varillas_x.append(i * s_x + e + rx)
        for i in range(self.numero_aceros_y):
            varillas_y.append(i * s_y + e + ry)
        varillas_y.pop(0)
        varillas_y.pop(-1)
        
        vx = varillas_x
        vy = varillas_y
        vy1 = []
        vy2 = []
        vx1 = []
        vx2 = []
        
        for i in range(self.numero_aceros_x):
            vy1.append(e + 1.2)
            vy2.append(h - e - 1.2)
        for i in range(self.numero_aceros_y - 2):
            vx1.append(e + 1.2)
            vx2.append(b - e - 1.2)
            
        # PLOTEO DE SECCION DE LA COLUMNA
        ax3 = plt.subplot(1, 3, 3)
        ax3.plot(rectangulo_x, rectangulo_y, "k-")
        ax3.plot(vx, vy1, "ko", ms=13)
        ax3.plot(vx, vy2, "ko", ms=13)
        ax3.plot(vx1, vy, "ko", ms=13)
        ax3.plot(vx2, vy, "ko", ms=13)
        ax3.plot(estribo_x, estribo_y, linestyle='-', linewidth=3.5)
        ax3.set_title("Seccion de la columna " + str(self.etiqueta), fontweight="bold")
        plt.xlabel("Luis Maldonado")
        ax3.set_facecolor("lightgray")
        ax3.set(xlim=(0, b), ylim=(0, h))
        
        label = [
            "$base$ = " + str(self.base) + "$ cm$" + '\n$altura$ = ' + str(self.altura) + "$ cm$" + 
            '\n$f´_{c} $= ' + str(self.fc) + "$kg/cm^2$" + 
            '\n$Φ$ = ' + str(self.diametro) + 
            '\n$cuantia$ = ' + str(round(self.cuantia * 100, 2)) + "%"
        ]
        
        ax3.legend(
            label, 
            loc='center left', 
            bbox_to_anchor=(0.96, 0.5), 
            frameon=False, 
            title="   $PROPIEDADES$", 
            fontsize=12
        )
        
        plt.tight_layout()
        plt.show()