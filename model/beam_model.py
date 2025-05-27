class BeamModel:
    def __init__(self):
        # Propiedades básicas
        self.L = None  # Luz (m)
        self.b = None  # Ancho (m)
        self.h = None  # Altura (m)
        self.d = None  # Altura efectiva (m)
        self.fc = None  # Resistencia concreto (MPa)
        self.fy = None  # Resistencia acero (MPa)
        self.fyv = None  # Resistencia estribos (MPa)

        # Cargas
        self.cargas_muertas = None
        self.carga_viva = None
        self.carga_total = None
        self.carga_ultima_mayorada = None # Resistencia del acero para estribos (MPa)
        
        # Parámetros de diseño
        self.phi_v = 0.75  # Factor de reducción cortante

        # Datos para dibujo
        self.diametro_barra = None
        self.as_colocado = None
        self.area_barra = None

    def calcular_variables_auxiliares(self):
        """Calcula propiedades derivadas"""
        if None in [self.h, self.b, self.fc, self.fy, self.cargas_muertas, self.carga_viva]:
            raise ValueError("Faltan datos requeridos")
            
        self.d = self.h - 0.04  # Recubrimiento de 4cm
        self.fyv = self.fy if self.fyv is None else self.fyv
        self.carga_total = self.cargas_muertas + self.carga_viva
        self.carga_ultima_mayorada = 1.2*self.cargas_muertas + 1.6*self.carga_viva
        
    def validate_inputs(self):
        """Valida que todos los inputs necesarios estén presentes"""
        required = [self.L, self.t, self.h, self.b, self.fc, self.fy]
        return all(x is not None for x in required)
