# experto.py

# Base de conocimiento: Lista de diccionarios con las reglas de cada corte
BASE_CORTES = [
    {
        "nombre": "Textured Crop",
        "rostros": ["ovalado", "cuadrado", "diamante", "hexagonal"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Corto arriba con textura desconectada, flequillo corto desfilado."
    },
    {
        "nombre": "French Crop",
        "rostros": ["ovalado", "triángulo invertido", "redondo"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Flequillo recto a cejas, lados degradados, línea natural."
    },
    {
        "nombre": "Pompadour clásico",
        "rostros": ["ovalado", "cuadrado", "hexagonal", "diamante"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Volumen frontal elevado, laterales cortos, espalda cerrada."
    },
    {
        "nombre": "Modern Mullet",
        "rostros": ["diamante", "hexagonal", "alargado", "ovalado"],
        "cabellos": ["rizado", "afro", "ondulado"],
        "descripcion": "Corto en laterales/partera, largo en nuca con textura."
    },
    {
        "nombre": "Mid Fade + Quiff",
        "rostros": ["hexagonal", "diamante", "ovalado", "cuadrado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Degradado medio, mechón levantado pero controlado."
    },
    {
        "nombre": "High Fade + Pompadour",
        "rostros": ["redondo", "ovalado", "cuadrado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Máximo efecto alargador para rostros redondos."
    },
    {
        "nombre": "Curtains (cortina)",
        "rostros": ["diamante", "hexagonal", "alargado", "ovalado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Raya al medio, flequillo largo abriéndose a los lados."
    },
    {
        "nombre": "Side Swept Fringe",
        "rostros": ["triángulo invertido", "alargado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Flequillo largo peinado a un lado, oculta frente ancha."
    },
    {
        "nombre": "Buzz Cut",
        "rostros": ["alargado", "ovalado", "cuadrado"],
        "cabellos": ["todos", "liso", "ondulado", "rizado", "afro"],
        "descripcion": "Uniforme corto, equilibra caras largas."
    },
    {
        "nombre": "Flat Top",
        "rostros": ["redondo", "cuadrado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Superficie plana arriba, ángulos rectos, ideal para cejas anchas."
    },
    {
        "nombre": "Classic Taper",
        "rostros": ["alargado", "ovalado", "hexagonal", "diamante"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Degradado sutil, volumen lateral para caras largas."
    },
    {
        "nombre": "Caesar Crop",
        "rostros": ["alargado", "redondo", "ovalado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Flequillo recto corto, textura hacia adelante."
    },
    {
        "nombre": "Textured French Crop",
        "rostros": ["triángulo invertido", "ovalado"],
        "cabellos": ["rizado", "ondulado"],
        "descripcion": "Versión con microtextura para disimular frente ancha."
    },
    {
        "nombre": "Low Fade + Brushed Up",
        "rostros": ["cuadrado", "hexagonal", "diamante"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Cepillado hacia arriba y atrás, degradado bajo."
    },
    {
        "nombre": "Temple Fade + Volume Top",
        "rostros": ["diamante", "hexagonal", "ovalado"],
        "cabellos": ["liso", "rizado"],
        "descripcion": "Volumen solo en parte superior, lados muy ajustados."
    },
    {
        "nombre": "Drop Fade + Curly Top",
        "rostros": ["redondo", "cuadrado"],
        "cabellos": ["rizado", "afro"],
        "descripcion": "Degradado curvo detrás de oreja, rizos largos arriba."
    },
    {
        "nombre": "Afro Taper (redondeado)",
        "rostros": ["ovalado", "diamante", "hexagonal", "alargado"],
        "cabellos": ["afro"],
        "descripcion": "Forma de burbuja suave, degradado en nuca y patillas."
    },
    {
        "nombre": "Shaggy Crop",
        "rostros": ["alargado", "triángulo invertido"],
        "cabellos": ["ondulado", "rizado"],
        "descripcion": "Capas desconectadas, largo medio, despeine intencional."
    },
    {
        "nombre": "Slicked Back UnderCut",
        "rostros": ["hexagonal", "diamante", "ovalado"],
        "cabellos": ["liso", "ondulado"],
        "descripcion": "Laterales rapados, largo superior peinado hacia atrás."
    },
    {
        "nombre": "Mohawk sutil (desvanecido)",
        "rostros": ["redondo", "cuadrado", "ovalado"],
        "cabellos": ["liso", "ondulado", "rizado"],
        "descripcion": "Franja central de unos 5-7 cm, laterales en fade alto."
    }
]


# Función para ordenar la lista de resultados
def obtener_puntaje(elemento):
    return elemento["compatibilidad"]


# Motor de inferencia
def evaluar_cortes(rostro_usuario, cabello_usuario):
    rostro_usuario = rostro_usuario.lower()
    cabello_usuario = cabello_usuario.lower()

    resultados = []

    for corte in BASE_CORTES:
        puntaje = 0

        # Regla 1: Evaluación del rostro (Vale 60%)
        if rostro_usuario in corte["rostros"]:
            puntaje += 60

        # Regla 2: Evaluación del tipo de cabello (Vale 40%)
        if cabello_usuario in corte["cabellos"] or "todos" in corte["cabellos"]:
            puntaje += 40

        # Solo guardamos el corte si tiene al menos un 60% de compatibilidad
        if puntaje >= 60:
            nuevo_resultado = {
                "corte": corte["nombre"],
                "descripcion": corte["descripcion"],
                "compatibilidad": puntaje
            }
            resultados.append(nuevo_resultado)

    # Ordenamos de mayor a menor puntaje usando la funcion obtener_puntaje
    resultados.sort(key=obtener_puntaje, reverse=True)

    return resultados


# Código para probar si funciona directamente ejecutando este archivo
if __name__ == "__main__":
    prueba_rostro = "redondo"
    prueba_cabello = "liso"

    cortes_ideales = evaluar_cortes(prueba_rostro, prueba_cabello)

    print(f"Buscando cortes para rostro {prueba_rostro} y cabello {prueba_cabello}...\n")
    for r in cortes_ideales:
        print(f"- {r['corte']} ({r['compatibilidad']}% compatible)")
        print(f"  {r['descripcion']}\n")