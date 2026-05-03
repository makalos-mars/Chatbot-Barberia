from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# mensajes para que entienda el bot
X_train = [
    "quiero agendar una cita", "necesito un corte de pelo", "reserva para hoy", "dame un turno",
    "que corte me recomiendas", "que me queda mejor", "dame un consejo de imagen", "recomiendame un estilo"
]
y_train = [
    "agendar", "agendar", "agendar", "agendar",
    "consejo", "consejo", "consejo", "consejo"
]

# crear el modelo 
modelo_nlp = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('clf', MultinomialNB())
])

# Entrenar
modelo_nlp.fit(X_train, y_train)

def clasificar_intencion(texto):
    # predice la intención q tiene el usuario
    return modelo_nlp.predict([texto.lower()])[0]