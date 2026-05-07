# nlp.py
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# Corpus de entrenamiento


textos = [
    # Saludo
    "hola", "buenos dias", "buenas tardes", "que tal", "hey",
    "hola buenas", "que onda", "buen dia", "saludos",

    # Recomendación de corte → consejo
    "quiero una recomendacion",
    "no se que hacerme",
    "que corte me queda",
    "recomiendame un corte",
    "asesoria de imagen",
    "corte segun mi rostro",
    "ayuda con mi pelo",
    "dame un consejo",
    "que me recomiendas",
    "quiero saber que corte hacerme",
    "cual es el mejor corte para mi",
    "que estilo me va bien",
    "necesito una recomendacion de corte",

    # Agendar cita
    "quiero una cita",
    "apartar lugar",
    "tienen espacio",
    "agendar con mau",
    "quiero cortarme el pelo el viernes",
    "hay citas disponibles",
    "hacer reservacion",
    "quiero ir mañana",
    "sacar cita",
    "agendar",
    "quiero reservar",
    "hacer una cita",
    "necesito una cita",
]

etiquetas = [
    # saludo
    "saludo", "saludo", "saludo", "saludo", "saludo",
    "saludo", "saludo", "saludo", "saludo",

    # consejo
    "consejo", "consejo", "consejo", "consejo", "consejo",
    "consejo", "consejo", "consejo", "consejo", "consejo",
    "consejo", "consejo", "consejo",

    # agendar
    "agendar", "agendar", "agendar", "agendar", "agendar",
    "agendar", "agendar", "agendar", "agendar", "agendar",
    "agendar", "agendar", "agendar",
]

assert len(textos) == len(etiquetas), \
    f"Desajuste corpus: {len(textos)} textos vs {len(etiquetas)} etiquetas"

_modelo = make_pipeline(
    CountVectorizer(),
    MultinomialNB()
)

_modelo.fit(textos, etiquetas)

def clasificar_intencion(texto: str, umbral: float = 0.30) -> str:
    texto = texto.lower().strip()

    probs = _modelo.predict_proba([texto])[0]
    confianza = max(probs)

    if confianza < umbral:
        return "desconocido"

    return _modelo.predict([texto])[0]


def extraer_entidades(texto: str) -> dict:

    entidades = {}

    t = texto.lower().strip()

    mapa_rostros = {
        "ovalado": "ovalado",

        "redondo": "redondo",
        "redonda": "redondo",

        "cuadrado": "cuadrado",
        "cuadrada": "cuadrado",

        "alargado": "alargado",
        "alargada": "alargado",

        "diamante": "diamante",

        "hexagonal": "hexagonal",

        "triangulo invertido": "triángulo invertido",
        "triángulo invertido": "triángulo invertido",
    }

    for patron, canonico in mapa_rostros.items():
        if patron in t:
            entidades["rostro"] = canonico
            break

    mapa_cabello = {
        "liso": "liso",

        "ondulado": "ondulado",
        "ondulada": "ondulado",

        "rizado": "rizado",
        "rizada": "rizado",
        "rizos": "rizado",

        "afro": "afro",
    }

    for patron, canonico in mapa_cabello.items():
        if patron in t:
            entidades["cabello"] = canonico
            break

    mapa_mantenimiento = {
        "bajo": "bajo",
        "poco": "bajo",
        "mínimo": "bajo",
        "minimo": "bajo",
        "nada": "bajo",

        "medio": "medio",
        "regular": "medio",
        "normal": "medio",
        "moderado": "medio",

        "alto": "alto",
        "mucho": "alto",
        "intenso": "alto",
        "diario": "alto",
    }

    for patron, canonico in mapa_mantenimiento.items():
        if patron in t:
            entidades["mantenimiento"] = canonico
            break

    barberos = ["mau", "tony", "riatana", "yahir"]

    for b in barberos:
        if b in t:
            entidades["barbero"] = b.upper()
            break

    dias = [
        "lunes",
        "martes",
        "miercoles",
        "miércoles",
        "jueves",
        "viernes",
        "sabado",
        "sábado",
        "domingo",
    ]

    for d in dias:
        if d in t:
            entidades["dia"] = d
            break

    numeros = re.findall(r"\d+", t)

    if numeros:
        entidades["valor"] = float(numeros[0])

    return entidades