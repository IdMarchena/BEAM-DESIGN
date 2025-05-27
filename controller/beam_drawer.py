import matplotlib.pyplot as plt
import math

class BeamDrawer:
    def __init__(self, b, h, rec, db, As_calculado, Ab):
        self.b = b          # Base de la viga (mm)
        self.h = h          # Altura de la viga (mm)
        self.rec = rec      # Recubrimiento (mm)
        self.db = db        # Diámetro de barra (mm)
        self.As_calculado = As_calculado  # Área de acero calculada (mm²)
        self.Ab = Ab        # Área de una barra (mm²)
        
    def draw(self):
        fig, ax = plt.subplots(figsize=(12, 4))
        # Dibujar la viga
        ax.plot([0, self.b], [0, 0], color='black', linewidth=2)  # Línea inferior
        ax.plot([0, self.b], [self.h, self.h], color='black', linewidth=2)  # Línea superior
        ax.plot([0, 0], [0, self.h], color='black', linewidth=2)  # Extremo izquierdo
        ax.plot([self.b, self.b], [0, self.h], color='black', linewidth=2)  # Extremo derecho

        # Dibujar el estribo
        ax.add_patch(plt.Rectangle((self.rec, self.rec), self.b - 2 * self.rec, self.h - 2 * self.rec, edgecolor='green', facecolor='none', linestyle='-', linewidth=1))

        # Dibujar las barras de acero longitudinal
        num_barras = max(1, math.ceil(self.As_calculado / self.Ab))  # Aproximación del número de barras
        espacio_efectivo = self.b - 2 * (self.rec + self.db / 2)  # Espacio útil para las barras
        espaciado_barras = espacio_efectivo / (num_barras - 1) if num_barras > 1 else 0
        x_inicial = self.rec + self.db / 2  # Primera barra con margen desde el recubrimiento

        for i in range(num_barras):
            x = x_inicial + i * espaciado_barras
            ax.add_patch(plt.Circle((x, self.rec + self.db / 2), self.db / 2, color='blue'))

        # Configurar el gráfico
        ax.set_xlim(0, self.b)
        ax.set_ylim(0, self.h)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title("Plano 2D de la Viga Diseñada")
        plt.xlabel("Base (mm)")
        plt.ylabel("Altura (mm)")
        plt.show()

        # Imprimir detalles de las barras
        print(f"No. de barras: {num_barras}")
        print(f"Espaciado entre barras: {espaciado_barras:.2f} mm")
