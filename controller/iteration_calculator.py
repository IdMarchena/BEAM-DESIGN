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
        
        # Calculos iniciales
        self.dprima = recubrimiento                        # d´
        self.peralte_efectivo = altura - recubrimiento     # d
        self.altura_efectiva = altura - 2 * recubrimiento
        self.altura_espaciamiento = self.altura_efectiva / (numero_aceros_y - 1)
        self.Ag = base * altura
        self.numero_aceros = 2 * (numero_aceros_x) + 2 * (numero_aceros_y) - 4

        self.εc = 0.003   # Deformacion maxima del concreto
        self.εy = fy / Es # Deformacion maxima del acero

        # Calculos de las distancias de cada varilla
        self.distancias = []
        for i in range(numero_aceros_y):
            self.distancias.append(self.altura_espaciamiento * i + recubrimiento)
        self.distancias2 = list(self.distancias)  
        
        # Calculo de areas de acero
        if self.diametro == "1/4":
            self.As1 = 0.32
        elif self.diametro == "3/8":
            self.As1 = 0.71
        elif self.diametro == "1/2":
            self.As1 = 1.27
        elif self.diametro == "5/8":
            self.As1 = 1.98
        elif self.diametro == "3/4":
            self.As1 = 2.84
        elif self.diametro == "1":
            self.As1 = 5.10  # 5.07

        self.Areas_nn = [0 for i in range(numero_aceros_y)]
        for i in range(numero_aceros_y):
            if i == 0 or i == (numero_aceros_y - 1):
                self.Areas_nn[i] = self.As1 * (numero_aceros_x)
            else:
                self.Areas_nn[i] = self.As1 * 2.00
                
        # Beta 1 
        if fc < 280:
            self.beta1 = 0.85
        else:
            self.beta1 = max(0.85 - 0.05 * (fc - 280) / 7, 0.65)

        self.cuantia = sum(self.Areas_nn) / self.Ag
        
        # Calcular diagramas de interacción
        self.calcular_diagramas()
        
        # Generar gráficos
        self.generar_graficas()
    
    def phi_ACI(self, εs, εy):
        phi_factor = 0.65 + 0.25 * (εs - εy) / (0.005 - εy)
        if phi_factor >= 0.90:
            phi = 0.90        # Controlado por la Tension
        elif phi_factor <= 0.65:
            phi = 0.65        # Controlado por la Compresion
        else:
            phi = phi_factor  # Transicion
        return phi

    def phi_E060(self, Suma_Tensiones_normales):
        phi = 0.65
        if Suma_Tensiones_normales > 0.1 * (self.base * self.altura) * self.fc:
            phi = 0.65
        elif Suma_Tensiones_normales > 0:
            phi = 0.9 - 2 / (self.fc * self.Ag) * Suma_Tensiones_normales
        else:
            phi = 0.9
        return phi

    def Diagrama_interaccion_ACI(self, c):
        εsi = [0 for i in range(self.numero_aceros_y)] 
        fsi = [0 for i in range(self.numero_aceros_y)] 
        Cc = [0 for i in range(self.numero_aceros_y)] 
        BP = [0 for i in range(self.numero_aceros_y)] 
        MP = [0 for i in range(self.numero_aceros_y)] 

        # Deformacion de la fibra de acero:
        for i in range(self.numero_aceros_y):
            if c > self.distancias2[i]:
                εsi[i] = self.εc * (c - self.distancias2[i]) / c
            else:
                εsi[i] = self.εc * (self.distancias2[i] - c) / c 

        # Esfuerzo del acero:
        for i in range(self.numero_aceros_y):    
            if εsi[i] <= self.εy:
                fsi[i] = self.Es * εsi[i]
            else:
                fsi[i] = self.fy

        # Fuerza del acero
        for i in range(self.numero_aceros_y):
            if c > self.distancias2[i] or i == 0:        
                Cc[i] = self.Areas_nn[i] * fsi[i]
            else:
                Cc[i] = -1 * self.Areas_nn[i] * fsi[i]

        # Distancias de los aceros al Centroide Plastico:
        for i in range(self.numero_aceros_y):
            if self.altura * 0.5 > self.distancias2[i]:               
                BP[i] = 0.5 * self.altura - self.distancias2[i]         # COMPRESION
            else:
                BP[i] = self.distancias2[i] - 0.5 * self.altura         # TRACCION

        # Momentos de la fuerza de los aceros con respecto al Centroide Plastico
        for i in range(self.numero_aceros_y):
            if self.distancias2[i] > 0.5 * self.altura or BP[i] * Cc[i] < 0:
                MP[i] = -1 * BP[i] * Cc[i]
            else:
                MP[i] = BP[i] * Cc[i]

        F_concreto = 0.85 * self.fc * (0.85 * c) * self.base
        M_concreto = F_concreto * (self.altura * 0.5 - 0.85 * c * 0.5)  
        Cc.append(F_concreto)
        MP.append(M_concreto)

        Suma_Tensiones_normales = sum(Cc)
        Suma_Momentos_normales = sum(MP)

        phi = self.phi_ACI(εsi[-1], self.εy)  
        PU = np.array(Suma_Tensiones_normales) * phi
        MU = np.array(Suma_Momentos_normales) * phi

        return Suma_Tensiones_normales, PU, Suma_Momentos_normales, MU

    def Diagrama_interaccion_E060(self, c):
        εsi = [0 for i in range(self.numero_aceros_y)] 
        fsi = [0 for i in range(self.numero_aceros_y)] 
        Cc = [0 for i in range(self.numero_aceros_y)] 
        BP = [0 for i in range(self.numero_aceros_y)] 
        MP = [0 for i in range(self.numero_aceros_y)] 

        # Deformacion de la fibra de acero:
        for i in range(self.numero_aceros_y):
            if c > self.distancias2[i]:
                εsi[i] = self.εc * (c - self.distancias2[i]) / c
            else:
                εsi[i] = self.εc * (self.distancias2[i] - c) / c 

        # Esfuerzo del acero:
        for i in range(self.numero_aceros_y):    
            if εsi[i] <= self.εy:
                fsi[i] = self.Es * εsi[i]
            else:
                fsi[i] = self.fy

        # Fuerza del acero
        for i in range(self.numero_aceros_y):
            if c > self.distancias2[i] or i == 0:       
                Cc[i] = self.Areas_nn[i] * fsi[i]
            else:
                Cc[i] = -1 * self.Areas_nn[i] * fsi[i]

        # Distancias de los aceros al Centroide Plastico:
        for i in range(self.numero_aceros_y):
            if self.altura * 0.5 > self.distancias2[i]:               
                BP[i] = 0.5 * self.altura - self.distancias2[i]         # COMPRESION
            else:
                BP[i] = self.distancias2[i] - 0.5 * self.altura         # TRACCION

        # Momentos de la fuerza de los aceros con respecto al Centroide Plastico
        for i in range(self.numero_aceros_y):
            if self.distancias2[i] > 0.5 * self.altura or BP[i] * Cc[i] < 0:
                MP[i] = -1 * BP[i] * Cc[i]
            else:
                MP[i] = BP[i] * Cc[i]

        F_concreto = 0.85 * self.fc * (0.85 * c) * self.base
        M_concreto = F_concreto * (self.altura * 0.5 - 0.85 * c * 0.5)  
        Cc.append(F_concreto)
        MP.append(M_concreto)

        Suma_Tensiones_normales = sum(Cc)
        Suma_Momentos_normales = sum(MP)

        phi = self.phi_E060(Suma_Tensiones_normales)

        PU = np.array(Suma_Tensiones_normales) * phi
        MU = np.array(Suma_Momentos_normales) * phi

        return Suma_Tensiones_normales, PU, Suma_Momentos_normales, MU

    def calcular_diagramas(self):
        Ast = self.numero_aceros * self.As1
        Pn = (0.85 * self.fc * (self.Ag - Ast) + Ast * self.fy)
        Pnmax = 0.75 * Pn  # Para columnas con estribos
        Pumax = 0.65 * Pnmax              
        PCPN = [0, Pnmax]
        PCPU = [0, Pumax]
        
        # Inicializar listas para ACI
        self.carga_nom_ACI = []
        self.carga_ult_ACI = []
        self.momento_nom_ACI = []
        self.momento_ult_ACI = []

        valores_c = np.arange(self.altura + self.altura/4, self.recubrimiento, -0.5)
        for c in valores_c:
            CN_ACI, CU_ACI, MN_ACI, MU_ACI = self.Diagrama_interaccion_ACI(c)
            self.carga_nom_ACI.append(CN_ACI)
            self.carga_ult_ACI.append(CU_ACI)
            self.momento_nom_ACI.append(MN_ACI)
            self.momento_ult_ACI.append(MU_ACI)
            
        # Inicializar listas para E060
        self.carga_nom_E060 = []
        self.carga_ult_E060 = []
        self.momento_nom_E060 = []
        self.momento_ult_E060 = []

        for c in valores_c:
            CN_E060, CU_E060, MN_E060, MU_E060 = self.Diagrama_interaccion_E060(c)
            self.carga_nom_E060.append(CN_E060)
            self.carga_ult_E060.append(CU_E060)
            self.momento_nom_E060.append(MN_E060)
            self.momento_ult_E060.append(MU_E060)
            
        P_T = -Ast * self.fy
        Mn_T = 0.00
        TP = [Mn_T, P_T]
        TPU = [0.9 * Mn_T, 0.9 * P_T]
        
        # Punto de falla balanceada
        Cb = (6000.00 * self.peralte_efectivo) / (6000.00 + self.fy)
        Pn_bal, Pu_bal, Mn_bal, Mu_bal = self.Diagrama_interaccion_ACI(Cb)
        self.carga_nom_bal = [Pn_bal, 0]
        self.momento_nom_bal = [Mn_bal, 0]
        
        # Ajustar diagramas ACI
        self.carga_nom_r_ACI = [i for i in self.carga_nom_ACI]
        self.carga_ult_r_ACI = [i for i in self.carga_ult_ACI]
        self.momento_nom_r_ACI = [i for i in self.momento_nom_ACI]
        self.momento_ult_r_ACI = [i for i in self.momento_ult_ACI]



        for i in range(len(self.carga_ult_ACI)):
            if self.carga_ult_ACI[i] >= Pumax:
                self.carga_ult_r_ACI[i] = Pumax  

        # Añadir punto de tracción pura ACI
        self.carga_nom_r_ACI.append(P_T)     
        self.momento_nom_r_ACI.append(0)
        self.carga_ult_r_ACI.append(0.9 * P_T)
        self.momento_ult_r_ACI.append(0)
        
        # Ajustar diagramas E060
        self.carga_nom_r_E060 = [i for i in self.carga_nom_E060]
        self.carga_ult_r_E060 = [i for i in self.carga_ult_E060]
        self.momento_nom_r_E060 = [i for i in self.momento_nom_E060]
        self.momento_ult_r_E060 = [i for i in self.momento_ult_E060]



        for i in range(len(self.carga_ult_E060)):
            if self.carga_ult_E060[i] >= Pumax:
                self.carga_ult_r_E060[i] = Pumax  

        # Añadir punto de tracción pura E060
        self.carga_nom_r_E060.append(P_T)     
        self.momento_nom_r_E060.append(0)
        self.carga_ult_r_E060.append(0.9 * P_T)
        self.momento_ult_r_E060.append(0)

    def generar_graficas(self):
        # ACI
        fig = plt.figure(figsize=(21, 10))
        ax1 = plt.subplot(1, 3, 1)
        ax1.plot(np.array(self.momento_nom_bal)/100000, np.array(self.carga_nom_bal)/1000, linestyle='--', color="black", linewidth=1, alpha=0.4)
        ax1.plot(np.array(self.momento_nom_ACI)/100000, np.array(self.carga_nom_ACI)/1000, linestyle='--', color="silver")
        C_N, = ax1.plot(np.array(self.momento_nom_r_ACI)/100000, np.array(self.carga_nom_r_ACI)/1000, linestyle='-', color="black")
        ax1.plot(np.array(self.momento_ult_ACI)/100000, np.array(self.carga_ult_ACI)/1000, linestyle='--', color="lightcoral")
        C_D, = ax1.plot(np.array(self.momento_ult_r_ACI)/100000, np.array(self.carga_ult_r_ACI)/1000, linestyle='-', color="red")
    
        ax1.plot(self.carga_momento, self.carga_compresion, "kx", ms=9)
        ax1.set_ylabel("P (ton)")
        ax1.set_xlabel("M (ton.m)")
        ax1.set_title("DIAGRAMA DE INTERACCION ACI 318-19", fontweight="bold")
        ax1.legend((C_N, C_D), ("Curva Nominal Teorica", "Curva Diseño ACI 318"), loc='upper right', shadow=True)
        ax1.grid(linewidth=0.6)
        ax1.set(xlim=(0))
        plt.axis("on")
        ax1.set_facecolor("white")
    
        # E060
        ax2 = plt.subplot(1, 3, 2)
        ax2.plot(np.array(self.momento_nom_bal)/100000, np.array(self.carga_nom_bal)/1000, linestyle='--', color="black", linewidth=1, alpha=0.4)
        ax2.plot(np.array(self.momento_nom_E060)/100000, np.array(self.carga_nom_E060)/1000, linestyle='--', color="silver")
        C_N, = ax2.plot(np.array(self.momento_nom_r_E060)/100000, np.array(self.carga_nom_r_E060)/1000, linestyle='-', color="black")
        ax2.plot(np.array(self.momento_ult_E060)/100000, np.array(self.carga_ult_E060)/1000, linestyle='--', color="lightcoral")
        C_D, = ax2.plot(np.array(self.momento_ult_r_E060)/100000, np.array(self.carga_ult_r_E060)/1000, linestyle='-', color="red")
        ax2.plot(self.carga_momento, self.carga_compresion, "kx", ms=9)
        ax2.set_ylabel("P (ton)")
        ax2.set_xlabel("M (ton.m)")
        ax2.set_title("DIAGRAMA DE INTERACCION E060", fontweight="bold")
        ax2.legend((C_N, C_D), ("Curva Nominal Teorica", "Curva Diseño E060"), loc='upper right', shadow=True)
        ax2.grid(linewidth=0.6)
        ax2.set(xlim=(0))
        plt.axis("on")
        ax2.set_facecolor("white")
    
        # SECCION
        # variables y operaciones para definir la geometria de la seccion de la columna
        b = self.base
        h = self.altura
        e = self.recubrimiento       # cm  # recubrimiento
        rx = 1.2      # variable, hace referencias al diametro en el plot
        ry = 0.9
        rectangulo_x = [0, b, b, 0, 0]
        rectangulo_y = [0, 0, h, h, 0]
        estribo_x = [e, b-e, b-e, e, e]
        estribo_y = [e, e, h-e, h-e, e]
        k_x = self.numero_aceros_x - 1
        k_y = self.numero_aceros_y - 1
        s_x = (b - 2*e - 2*rx) / k_x
        s_y = (h - 2*e - 2*ry) / k_y
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
        ax3.set_title("Seccion de la columna  " + str(self.etiqueta), fontweight="bold")
        
        ax3.set_facecolor("lightgray")
        ax3.set(xlim=(0, b), ylim=(0, h))
        
        label = ["$base$ = " + str(self.base) + "$ cm$" + 
                '\n$altura$ = ' + str(self.altura) + "$ cm$" + 
                '\n$f´_{c} $= ' + str(self.fc) + "$kg/cm^2$" + 
                '\n$Φ$ = ' + str(self.diametro) + 
                '\n$cuantia$ = ' + str(round(self.cuantia*100, 2)) + "%"]
                
        ax3.legend(label, loc='center left', bbox_to_anchor=(0.96, 0.5), 
                  frameon=False, title="   $PROPIEDADES$", fontsize=12)
        plt.show()