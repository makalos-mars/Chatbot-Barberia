
# Funciones de membresía


def _tri(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c:
        return 0.0
    return (x - a) / (b - a) if x <= b else (c - x) / (c - b)


def _trap(x: float, a: float, b: float, c: float, d: float) -> float:
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    return (x - a) / (b - a) if x < b else (d - x) / (d - c)


# Conjuntos de entrada compat_rostro / compat_cabello  [0, 1]
def _baja(x):  return _trap(x, 0.0, 0.0, 0.20, 0.50)
def _media(x): return _tri(x,  0.25, 0.50, 0.75)
def _alta(x):  return _trap(x, 0.50, 0.80, 1.00, 1.00)

# Conjuntos de entrada gap_mantenimiento  [0, 1]
def _gm_bajo(x):  return _trap(x, 0.00, 0.00, 0.15, 0.35)
def _gm_medio(x): return _tri(x,  0.25, 0.50, 0.75)
def _gm_alto(x):  return _trap(x, 0.65, 0.85, 1.00, 1.00)

# Conjuntos de salida puntuacion  [0, 100]
_SALIDA = {
    "muy_baja": lambda x: _trap(x,  0,  0, 10, 25),
    "baja":     lambda x: _tri(x,  15, 30, 45),
    "media":    lambda x: _tri(x,  35, 50, 65),
    "alta":     lambda x: _tri(x,  55, 70, 85),
    "muy_alta": lambda x: _trap(x, 75, 90, 100, 100),
}


#  Base de conocimiento
# Cada corte tiene:
#   rostros (permite compatibilidad parcial)
#   cabellos {tipo:  grado [0,1]}
#   mantenimiento (0=sin mantenimiento, 1=diario)

BASE_CORTES: list[dict] = [
    {
        "nombre": "Textured Crop",
        "rostros":  {"ovalado": 1.0, "cuadrado": 1.0, "diamante": 0.8,
                     "hexagonal": 0.8, "redondo": 0.3, "alargado": 0.3, "triángulo invertido": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 1.0, "rizado": 0.4, "afro": 0.2},
        "mantenimiento": 0.5,
        "descripcion": "Corto arriba con textura desconectada, flequillo corto desfilado.",
    },
    {
        "nombre": "French Crop",
        "rostros":  {"ovalado": 1.0, "triángulo invertido": 1.0, "redondo": 1.0,
                     "cuadrado": 0.5, "alargado": 0.4, "diamante": 0.5, "hexagonal": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.3, "afro": 0.2},
        "mantenimiento": 0.3,
        "descripcion": "Flequillo recto a cejas, lados degradados, línea natural.",
    },
    {
        "nombre": "Pompadour clásico",
        "rostros":  {"ovalado": 1.0, "cuadrado": 1.0, "hexagonal": 1.0, "diamante": 0.8,
                     "redondo": 0.5, "alargado": 0.4, "triángulo invertido": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.4, "afro": 0.2},
        "mantenimiento": 0.85,
        "descripcion": "Volumen frontal elevado, laterales cortos, espalda cerrada.",
    },
    {
        "nombre": "Modern Mullet",
        "rostros":  {"diamante": 1.0, "hexagonal": 0.9, "alargado": 1.0, "ovalado": 0.8,
                     "cuadrado": 0.4, "redondo": 0.3, "triángulo invertido": 0.5},
        "cabellos": {"rizado": 1.0, "afro": 0.9, "ondulado": 1.0, "liso": 0.5},
        "mantenimiento": 0.6,
        "descripcion": "Corto en laterales/partera, largo en nuca con textura.",
    },
    {
        "nombre": "Mid Fade + Quiff",
        "rostros":  {"hexagonal": 1.0, "diamante": 0.9, "ovalado": 1.0, "cuadrado": 1.0,
                     "redondo": 0.5, "alargado": 0.4, "triángulo invertido": 0.4},
        "cabellos": {"liso": 1.0, "ondulado": 1.0, "rizado": 0.5, "afro": 0.3},
        "mantenimiento": 0.6,
        "descripcion": "Degradado medio, mechón levantado pero controlado.",
    },
    {
        "nombre": "High Fade + Pompadour",
        "rostros":  {"redondo": 1.0, "ovalado": 1.0, "cuadrado": 0.9,
                     "alargado": 0.3, "diamante": 0.5, "hexagonal": 0.5, "triángulo invertido": 0.4},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.4, "afro": 0.2},
        "mantenimiento": 0.8,
        "descripcion": "Máximo efecto alargador para rostros redondos.",
    },
    {
        "nombre": "Curtains (cortina)",
        "rostros":  {"diamante": 1.0, "hexagonal": 0.9, "alargado": 1.0, "ovalado": 0.9,
                     "cuadrado": 0.4, "redondo": 0.3, "triángulo invertido": 0.6},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.4, "afro": 0.2},
        "mantenimiento": 0.4,
        "descripcion": "Raya al medio, flequillo largo abriéndose a los lados.",
    },
    {
        "nombre": "Side Swept Fringe",
        "rostros":  {"triángulo invertido": 1.0, "alargado": 1.0, "ovalado": 0.6,
                     "redondo": 0.3, "cuadrado": 0.3, "diamante": 0.4, "hexagonal": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 0.8, "rizado": 0.3, "afro": 0.1},
        "mantenimiento": 0.4,
        "descripcion": "Flequillo largo peinado a un lado, oculta frente ancha.",
    },
    {
        "nombre": "Buzz Cut",
        "rostros":  {"alargado": 1.0, "ovalado": 1.0, "cuadrado": 0.9,
                     "redondo": 0.5, "diamante": 0.5, "hexagonal": 0.5, "triángulo invertido": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 1.0, "rizado": 1.0, "afro": 0.9},
        "mantenimiento": 0.1,
        "descripcion": "Uniforme corto, equilibra visualmente caras largas.",
    },
    {
        "nombre": "Flat Top",
        "rostros":  {"redondo": 1.0, "cuadrado": 1.0, "ovalado": 0.6,
                     "alargado": 0.3, "diamante": 0.4, "hexagonal": 0.4, "triángulo invertido": 0.4},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.5, "afro": 0.4},
        "mantenimiento": 0.7,
        "descripcion": "Superficie plana arriba, ángulos rectos, ideal para frentes anchas.",
    },
    {
        "nombre": "Classic Taper",
        "rostros":  {"alargado": 1.0, "ovalado": 1.0, "hexagonal": 1.0, "diamante": 0.9,
                     "cuadrado": 0.5, "redondo": 0.4, "triángulo invertido": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.4, "afro": 0.3},
        "mantenimiento": 0.3,
        "descripcion": "Degradado sutil, añade volumen lateral para caras largas.",
    },
    {
        "nombre": "Caesar Crop",
        "rostros":  {"alargado": 1.0, "redondo": 1.0, "ovalado": 0.9,
                     "cuadrado": 0.5, "diamante": 0.4, "hexagonal": 0.5, "triángulo invertido": 0.5},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.3, "afro": 0.2},
        "mantenimiento": 0.3,
        "descripcion": "Flequillo recto corto, textura hacia adelante.",
    },
    {
        "nombre": "Textured French Crop",
        "rostros":  {"triángulo invertido": 1.0, "ovalado": 1.0, "redondo": 0.7,
                     "cuadrado": 0.4, "alargado": 0.4, "diamante": 0.5, "hexagonal": 0.5},
        "cabellos": {"rizado": 1.0, "ondulado": 1.0, "liso": 0.5, "afro": 0.4},
        "mantenimiento": 0.4,
        "descripcion": "Microtextura que disimula frente ancha.",
    },
    {
        "nombre": "Low Fade + Brushed Up",
        "rostros":  {"cuadrado": 1.0, "hexagonal": 1.0, "diamante": 0.9, "ovalado": 0.7,
                     "redondo": 0.4, "alargado": 0.3, "triángulo invertido": 0.4},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.4, "afro": 0.3},
        "mantenimiento": 0.5,
        "descripcion": "Cepillado hacia arriba y atrás, degradado bajo.",
    },
    {
        "nombre": "Temple Fade + Volume Top",
        "rostros":  {"diamante": 1.0, "hexagonal": 1.0, "ovalado": 0.9,
                     "cuadrado": 0.5, "redondo": 0.4, "alargado": 0.4, "triángulo invertido": 0.5},
        "cabellos": {"liso": 1.0, "rizado": 1.0, "ondulado": 0.7, "afro": 0.5},
        "mantenimiento": 0.6,
        "descripcion": "Volumen solo en parte superior, lados muy ajustados.",
    },
    {
        "nombre": "Drop Fade + Curly Top",
        "rostros":  {"redondo": 1.0, "cuadrado": 1.0, "ovalado": 0.7,
                     "alargado": 0.3, "diamante": 0.4, "hexagonal": 0.4, "triángulo invertido": 0.4},
        "cabellos": {"rizado": 1.0, "afro": 1.0, "ondulado": 0.5, "liso": 0.3},
        "mantenimiento": 0.5,
        "descripcion": "Degradado curvo detrás de oreja, rizos largos arriba.",
    },
    {
        "nombre": "Afro Taper",
        "rostros":  {"ovalado": 1.0, "diamante": 1.0, "hexagonal": 0.9, "alargado": 1.0,
                     "cuadrado": 0.5, "redondo": 0.4, "triángulo invertido": 0.5},
        "cabellos": {"afro": 1.0, "rizado": 0.6, "ondulado": 0.3, "liso": 0.1},
        "mantenimiento": 0.3,
        "descripcion": "Forma de burbuja suave, degradado en nuca y patillas.",
    },
    {
        "nombre": "Shaggy Crop",
        "rostros":  {"alargado": 1.0, "triángulo invertido": 1.0, "ovalado": 0.7,
                     "redondo": 0.3, "cuadrado": 0.3, "diamante": 0.5, "hexagonal": 0.5},
        "cabellos": {"ondulado": 1.0, "rizado": 1.0, "liso": 0.5, "afro": 0.4},
        "mantenimiento": 0.5,
        "descripcion": "Capas desconectadas, largo medio, despeine intencional.",
    },
    {
        "nombre": "Slicked Back UnderCut",
        "rostros":  {"hexagonal": 1.0, "diamante": 1.0, "ovalado": 0.9,
                     "cuadrado": 0.5, "alargado": 0.4, "redondo": 0.3, "triángulo invertido": 0.4},
        "cabellos": {"liso": 1.0, "ondulado": 0.9, "rizado": 0.4, "afro": 0.2},
        "mantenimiento": 0.7,
        "descripcion": "Laterales rapados, largo superior peinado hacia atrás.",
    },
    {
        "nombre": "Mohawk sutil",
        "rostros":  {"redondo": 1.0, "cuadrado": 1.0, "ovalado": 0.9,
                     "diamante": 0.5, "hexagonal": 0.5, "alargado": 0.3, "triángulo invertido": 0.4},
        "cabellos": {"liso": 1.0, "ondulado": 1.0, "rizado": 0.9, "afro": 0.5},
        "mantenimiento": 0.6,
        "descripcion": "Franja central de 5-7 cm, laterales en fade alto.",
    },
]


# Motor difuso (Mamdani)

class _SistemaFuzzy:
    # 9 reglas de compatibilidad
    _REGLAS_COMPAT = [
        ("alta",  "alta",  "muy_alta"),
        ("alta",  "media", "alta"),
        ("media", "alta",  "alta"),
        ("alta",  "baja",  "media"),
        ("baja",  "alta",  "media"),
        ("media", "media", "media"),
        ("media", "baja",  "baja"),
        ("baja",  "media", "baja"),
        ("baja",  "baja",  "muy_baja"),
    ]

    # 3 reglas de ajuste por gap de mantenimiento (peso reducido = 0.30)
    _REGLAS_MANT = [
        ("bajo",  "alta",     0.30),   # match perfecto
        ("medio", "media",    0.20),   # match parcial
        ("alto",  "muy_baja", 0.30),   # mismatch alto
    ]

    _E = {"baja": _baja, "media": _media, "alta": _alta}
    _GM = {"bajo": _gm_bajo, "medio": _gm_medio, "alto": _gm_alto}

    def _disparar(self, cr: float, cc: float, gm: float) -> dict[str, float]:
        mu_cr = {k: f(cr) for k, f in self._E.items()}
        mu_cc = {k: f(cc) for k, f in self._E.items()}
        mu_gm = {k: f(gm) for k, f in self._GM.items()}

        act = {k: 0.0 for k in _SALIDA}

        # Reglas de compatibilidad
        for (er, ec, es) in self._REGLAS_COMPAT:
            disparo = min(mu_cr[er], mu_cc[ec])
            act[es] = max(act[es], disparo)

        # Reglas de mantenimiento
        for (em, es, peso) in self._REGLAS_MANT:
            disparo = mu_gm[em] * peso
            act[es] = max(act[es], disparo)

        return act

    @staticmethod
    def _centroide(act: dict[str, float], n: int = 200) -> float:
        num = den = 0.0
        for i in range(n + 1):
            y = i * 100.0 / n
            # Área acumulada = max de cada conjunto truncado a su nivel de activación
            mu = max(min(act[nombre], fn(y)) for nombre, fn in _SALIDA.items())
            num += mu * y
            den += mu
        return round(num / den, 1) if den > 0 else 0.0

    def evaluar(self, cr: float, cc: float, gm: float) -> float:
        return self._centroide(self._disparar(cr, cc, gm))


_fuzzy = _SistemaFuzzy()

def _etiqueta_mant(m: float) -> str:
    if m <= 0.33:  return "bajo"
    if m <= 0.66:  return "medio"
    return "alto"


def recomendar_cortes(
    rostro: str,
    cabello: str,
    mantenimiento_preferido: float = 0.5,   # 0 = ninguno, 1 = diario
    umbral: float = 38.0,
) -> list[dict]:
    rostro  = rostro.lower().strip()
    cabello = cabello.lower().strip()
    resultados = []

    for c in BASE_CORTES:
        cr  = c["rostros"].get(rostro, 0.0)
        cc  = c["cabellos"].get(cabello, 0.0)
        gm  = abs(mantenimiento_preferido - c["mantenimiento"])

        puntaje = _fuzzy.evaluar(cr, cc, gm)
        if puntaje >= umbral:
            resultados.append({
                "corte":          c["nombre"],
                "descripcion":    c["descripcion"],
                "puntuacion":     puntaje,
                "compat_rostro":  round(cr * 100),
                "compat_cabello": round(cc * 100),
                "mantenimiento":  _etiqueta_mant(c["mantenimiento"]),
            })

    resultados.sort(key=lambda x: x["puntuacion"], reverse=True)
    return resultados