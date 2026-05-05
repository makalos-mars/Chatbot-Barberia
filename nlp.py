from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Datos de entrenamiento corregidos y ampliados
X_train = [
    # --- AGENDAR ---
    "quiero agendar una cita",
    "necesito reservar un turno",
    "reserva para hoy",
    "dame un turno",
    "quiero hacer una cita",
    "puedo agendar para mañana",
    "quiero una cita para el lunes",
    "apartar lugar",
    "reservar hora",

    # --- CONSEJO ---
    "que corte me recomiendas",
    "que me queda mejor",
    "dame un consejo de imagen",
    "recomiendame un estilo",
    "recomendacion de corte",
    "necesito un corte de pelo",
    "que corte debo hacerme",
    "que estilo me va bien",
    "ayudame a elegir un corte",
    "quiero una recomendacion",
    "cual es el mejor corte para mi",
]

y_train = [
    # --- AGENDAR ---
    "agendar", "agendar", "agendar", "agendar", "agendar",
    "agendar", "agendar", "agendar", "agendar",

    # --- CONSEJO ---
    "consejo", "consejo", "consejo", "consejo", "consejo",
    "consejo", "consejo", "consejo", "consejo", "consejo",
    "consejo",
]

modelo_nlp = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('clf', MultinomialNB())
])

modelo_nlp.fit(X_train, y_train)

def clasificar_intencion(texto):
    return modelo_nlp.predict([texto.lower()])[0]