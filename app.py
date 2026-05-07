import chainlit as cl
import experto
import nlp
import agenda
import re

# Valores válidos
_ROSTROS = {
    "ovalado", "redondo", "cuadrado", "alargado",
    "diamante", "hexagonal", "triángulo invertido", "triangulo invertido",
}
_CABELLOS = {"liso", "ondulado", "rizado", "afro"}
_NO_SE = {
    "no lo se", "no sé", "nose", "no se", "no tengo idea",
    "desconozco", "ni idea", "no lo sé", "no sabo",
    "no sé cuál", "no se cual",
}
_MANT_MAP = {
    "bajo": 0.2, "poco": 0.2, "mínimo": 0.2, "minimo": 0.2, "nada": 0.1,
    "medio": 0.5, "regular": 0.5, "normal": 0.5, "moderado": 0.5,
    "alto": 0.8, "mucho": 0.8, "intenso": 0.8, "diario": 0.9,
}
_MANT_VALIDOS_SET = set(_MANT_MAP.keys())
_ETIQ_MANT = {0.1: "muy bajo", 0.2: "bajo", 0.5: "medio", 0.8: "alto", 0.9: "muy alto"}

# Palabras que indican que el texto NO es un nombre de persona
_PALABRAS_FUERA_DE_LUGAR = {
    "cita", "barbero", "corte", "pelo", "agendar", "reservar",
    "tenía", "tenia", "quiero", "necesito", "ya", "cancelar",
    "cambiar", "lunes", "martes", "miércoles", "jueves", "viernes",
    "pero", "porque", "aunque",
}


# Validadores

def _buscar_en(entrada: str, validos: set) -> str | None:
    e = entrada.lower().strip().replace("triangulo", "triángulo")
    return next((v for v in validos if v in e), None)


def _es_no_se(entrada: str) -> bool:
    e = entrada.lower().strip()
    return any(ns in e for ns in _NO_SE)


def _parsear_mantenimiento(texto: str) -> float | None:
    t = texto.lower()
    for kw, val in _MANT_MAP.items():
        if kw in t:
            return val
    return None


def _parece_nombre(texto: str) -> bool:
    """Un nombre real es corto y no contiene palabras de otro contexto."""
    palabras = texto.lower().split()
    if len(palabras) > 3:
        return False
    return not any(p in _PALABRAS_FUERA_DE_LUGAR for p in palabras)


#  Memoria de conversación
def _recordar(rol: str, texto: str) -> None:
    historial = cl.user_session.get("historial") or []
    historial.append({"rol": rol, "texto": texto})
    cl.user_session.set("historial", historial)


def _detectar_off_script(texto: str, estado_actual: str) -> str | None:
    intencion = nlp.clasificar_intencion(texto.lower())
    estados_agendado = {
        "esperando_nombre", "esperando_preferencia_barbero",
        "esperando_fecha", "esperando_hora", "esperando_hora_cualquiera",
    }
    if estado_actual in estados_agendado and intencion == "consejo":
        return (
            "Parece que quieres una recomendación de corte, "
            "pero estamos en medio del agendado. "
            "¿Continuamos con la cita o prefieres empezar de nuevo?"
        )
    return None


#  Utilidades generales

def parsear_fecha(texto: str) -> str | None:
    from datetime import datetime, timedelta
    texto = texto.lower().strip()
    hoy = datetime.today()

    dias_map = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6,
    }
    for nombre, num in dias_map.items():
        if nombre in texto:
            delta = (num - hoy.weekday()) % 7 or 7
            return (hoy + timedelta(days=delta)).strftime("%Y-%m-%d")

    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
        "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9,
        "octubre": 10, "noviembre": 11, "diciembre": 12,
    }
    for nombre, num in meses.items():
        if nombre in texto:
            try:
                dia = int("".join(filter(str.isdigit, texto)))
                return datetime(hoy.year, num, dia).strftime("%Y-%m-%d")
            except Exception:
                pass
    return None


def _horarios_por_barbero(slots: list[dict]) -> str:
    grupos: dict[str, list[str]] = {}
    for s in slots:
        grupos.setdefault(s["barbero"], []).append(s["hora"])
    lineas = [f"**{b}**: {', '.join(sorted(h))}" for b, h in grupos.items()]
    return "\n".join(lineas) if lineas else "Sin disponibilidad."


def _extraer_hora(texto: str) -> str:
    m = re.search(r"\b(\d{1,2}:\d{2})\b", texto)
    return m.group(1).zfill(5) if m else texto.strip()


# Inicio de sesión

@cl.on_chat_start
async def on_chat_start():
    for k in ("estado", "nombre", "barbero", "fecha",
              "corte_elegido", "mantenimiento"):
        cl.user_session.set(k, None)
    cl.user_session.set("historial", [])

    bienvenida = (
        "¡Bienvenido a la barbería! ¿En qué te puedo ayudar?\n\n"
        "- *'Quiero agendar una cita'*\n"
        "- *'Quiero una recomendación de corte'*"
    )
    _recordar("bot", bienvenida)
    await cl.Message(content=bienvenida).send()


# ─── Manejador principal

@cl.on_message
async def on_message(message: cl.Message):
    texto = message.content.strip()
    estado = cl.user_session.get("estado")

    _recordar("usuario", texto)

    #  Conversación finalizada
    if estado == "finalizado":
        cl.user_session.set("estado", None)
        resp = (
            "¿Algo más en lo que pueda ayudarte?\n\n"
            "- *'Quiero agendar una cita'*\n"
            "- *'Quiero una recomendación de corte'*"
        )
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
        return

    # Corte elegido
    if estado == "esperando_eleccion_corte":
        cl.user_session.set("corte_elegido", texto)
        cl.user_session.set("estado", "esperando_nombre")
        resp = "¡Excelente elección! Ahora agendemos tu cita.\n¿Cuál es tu nombre?"
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
        return

    # Nombre con validación
    if estado == "esperando_nombre":
        aviso = _detectar_off_script(texto, estado)
        if aviso:
            _recordar("bot", aviso)
            await cl.Message(content=aviso).send()
            return

        if not _parece_nombre(texto):
            resp = (
                f"Hmm, «{texto}» no parece un nombre. "
                "¿Cómo te llamas? (solo tu nombre, por ejemplo: *Carlos*, *Ana*)"
            )
            _recordar("bot", resp)
            await cl.Message(content=resp).send()
            return

        cl.user_session.set("nombre", texto)
        cl.user_session.set("estado", "esperando_preferencia_barbero")
        barberos = "**, **".join(agenda.BARBEROS_CONFIG.keys())
        resp = (
            f"Perfecto, {texto}. ¿Tienes preferencia de barbero "
            f"o te atendemos con cualquiera?\n\n"
            f"Nuestros barberos: **{barberos}**"
        )
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
        return

    #  Preferencia de barbero
    if estado == "esperando_preferencia_barbero":
        encontrado = next(
            (b for b in agenda.BARBEROS_CONFIG if b.lower() in texto.lower()),
            None,
        )
        cl.user_session.set("barbero", encontrado)
        cl.user_session.set("estado", "esperando_fecha")
        nombre_b = f"**{encontrado}**" if encontrado else "cualquier barbero disponible"
        resp = (
            f"Perfecto, con {nombre_b}.\n"
            "¿Qué día te gustaría venir? (ej: lunes, viernes, 10 de mayo…)"
        )
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
        return

    # Fecha
    if estado == "esperando_fecha":
        fecha_str = parsear_fecha(texto)
        if not fecha_str:
            resp = "No entendí la fecha. Prueba con *'lunes'*, *'viernes'* o *'10 de mayo'*."
            _recordar("bot", resp)
            await cl.Message(content=resp).send()
            return

        cl.user_session.set("fecha", fecha_str)
        barbero = cl.user_session.get("barbero")
        slots = agenda.buscar_disponibilidad(fecha_str, barbero=barbero)

        if not slots:
            resp = "No hay disponibilidad ese día. ¿Quieres intentar con otro día?"
            _recordar("bot", resp)
            await cl.Message(content=resp).send()
            return

        tabla = _horarios_por_barbero(slots)
        sig_est = "esperando_hora" if barbero else "esperando_hora_cualquiera"
        cl.user_session.set("estado", sig_est)
        resp = f"Horarios disponibles:\n\n{tabla}\n\n¿Cuál te viene mejor?"
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
        return

    #  Hora (barbero específico)
    if estado == "esperando_hora":
        hora = _extraer_hora(texto)
        fecha = cl.user_session.get("fecha")
        barbero = cl.user_session.get("barbero")
        exito, msg = agenda.agendar_cita(fecha, hora, barbero)
        await _confirmar_o_reintentar(exito, msg, fecha, barbero)
        return

    #  Hora (cualquier barbero)
    if estado == "esperando_hora_cualquiera":
        hora = _extraer_hora(texto)
        fecha = cl.user_session.get("fecha")
        slots = agenda.buscar_disponibilidad(fecha)
        barbero_asignado = next(
            (s["barbero"] for s in slots if s["hora"] == hora), None
        )
        if not barbero_asignado:
            resp = "Ese horario no está disponible. Intenta con otra hora."
            _recordar("bot", resp)
            await cl.Message(content=resp).send()
            return
        exito, msg = agenda.agendar_cita(fecha, hora, barbero_asignado)
        await _confirmar_o_reintentar(exito, msg, fecha, barbero_asignado)
        return

    # Clasificar intención
    intencion = nlp.clasificar_intencion(texto.lower())

    if intencion == "consejo":
        # Extraemos las entidades desde el primer mensaje y las pasamos al flujo
        entidades_iniciales = nlp.extraer_entidades(texto)
        await _flujo_recomendacion(entidades_iniciales)
    elif intencion == "agendar":
        cl.user_session.set("estado", "esperando_nombre")
        resp = "¡Con gusto! ¿Cuál es tu nombre?"
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
    elif intencion == "saludo":
        nombre = cl.user_session.get("nombre")
        saludo = f"¡Hola de nuevo, {nombre}!" if nombre else "¡Hola!"
        resp = (
            f"{saludo} ¿En qué te puedo ayudar?\n\n"
            "- *'Quiero agendar una cita'*\n"
            "- *'Quiero una recomendación de corte'*"
        )
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
    else:
        resp = (
            "No entendí bien. Puedes decirme:\n"
            "- *'Quiero agendar una cita'*\n"
            "- *'Quiero una recomendación de corte'*"
        )
        _recordar("bot", resp)
        await cl.Message(content=resp).send()


# Confirmación de cita

async def _confirmar_o_reintentar(exito: bool, msg: str,
                                  fecha: str, barbero: str) -> None:
    if exito:
        nombre = cl.user_session.get("nombre")
        corte = cl.user_session.get("corte_elegido")
        cl.user_session.set("estado", "finalizado")
        resp = (
            f"¡Listo, **{nombre}**! Tu cita quedó agendada:\n\n"
            f"**Día:** {fecha}\n"
            f"**Barbero:** {barbero}\n"
        )
        if corte:
            resp += f"**Corte:** {corte}\n"
        resp += "\n¡Te esperamos!"
    else:
        resp = f"{msg}\n\nIntenta con otro horario."

    _recordar("bot", resp)
    await cl.Message(content=resp).send()


# Wizard genérico con validación (una sola respuesta por turno)

async def _preguntar_con_validacion(
        pregunta_inicial: str,
        pregunta_reintento: str,
        pregunta_post_ayuda: str,
        validos: set,
        mensaje_ayuda: str,
) -> str | None:
    fase = "inicial"

    while True:
        if fase == "inicial":
            pregunta = pregunta_inicial
        elif fase == "post_ayuda":
            pregunta = pregunta_post_ayuda
        else:
            pregunta = pregunta_reintento

        r = await cl.AskUserMessage(content=pregunta).send()
        if not r:
            return None

        entrada = r["output"].strip()
        _recordar("usuario", entrada)

        if _es_no_se(entrada):
            _recordar("bot", mensaje_ayuda)
            await cl.Message(content=mensaje_ayuda).send()
            fase = "post_ayuda"
            continue

        valor = _buscar_en(entrada, validos)
        if valor:
            return valor

        fase = "reintento"


#  Wizard de recomendación

async def _flujo_recomendacion(entidades_prellenadas: dict = None) -> None:
    if entidades_prellenadas is None:
        entidades_prellenadas = {}

    # 1. Rostro
    rostro = entidades_prellenadas.get("rostro")

    if not rostro:
        rostro = await _preguntar_con_validacion(
            pregunta_inicial=(
                "¿Qué forma tiene tu rostro?\n"
                "*(ovalado, redondo, cuadrado, alargado, "
                "diamante, hexagonal, triángulo invertido)*"
            ),
            pregunta_reintento=(
                "No reconocí esa opción. Elige la que más se parezca:\n\n"
                "- **ovalado** — más largo que ancho, frente ligeramente más ancha\n"
                "- **redondo** — mejillas anchas, frente y mentón redondeados\n"
                "- **cuadrado** — mandíbula angular y frente ancha\n"
                "- **alargado** — claramente más largo que ancho\n"
                "- **diamante** — pómulos anchos, frente y mentón estrechos\n"
                "- **hexagonal** — sienes y mandíbula marcadas\n"
                "- **triángulo invertido** — frente muy ancha, mentón estrecho"
            ),
            pregunta_post_ayuda="¿Cuál de esas formas se parece más a la tuya?",
            validos=_ROSTROS,
            mensaje_ayuda=(
                "Sin problema, te doy algunas pistas:\n\n"
                "- Si tu cara parece un **huevo** → *ovalado*\n"
                "- Si es casi tan ancha como larga → *redondo*\n"
                "- Si tu mandíbula es **angular** → *cuadrado*\n"
                "- Si tu cara es muy **larga y estrecha** → *alargado*\n"
                "- Si tus **pómulos son lo más ancho** → *diamante*\n\n"
                "Escribe la que más se parezca."
            ),
        )
        if rostro is None:
            return

    #  2. Cabello
    cabello = entidades_prellenadas.get("cabello")

    if not cabello:
        cabello = await _preguntar_con_validacion(
            pregunta_inicial=(
                "¿Cómo es tu tipo de cabello?\n"
                "*(liso, ondulado, rizado, afro)*"
            ),
            pregunta_reintento=(
                "No reconocí ese tipo. Elige una opción:\n\n"
                "- **liso** — completamente recto, sin ondas\n"
                "- **ondulado** — tiene suaves curvas en forma de S\n"
                "- **rizado** — rizos definidos y en espiral\n"
                "- **afro** — muy rizado, esponjoso y apretado"
            ),
            pregunta_post_ayuda="¿Cuál de esos tipos describe mejor tu cabello?",
            validos=_CABELLOS,
            mensaje_ayuda=(
                "Te ayudo a identificarlo:\n\n"
                "- **liso** → si al secarlo queda totalmente recto\n"
                "- **ondulado** → si forma suaves curvas sin ser rizos\n"
                "- **rizado** → si tiene rizos definidos en espiral\n"
                "- **afro** → si es muy esponjoso y los rizos son apretados\n\n"
                "¿Cuál describe mejor tu cabello?"
            ),
        )
        if cabello is None:
            return

    # 3. Mantenimiento
    mant_texto = entidades_prellenadas.get("mantenimiento")

    if not mant_texto:
        mant_texto = await _preguntar_con_validacion(
            pregunta_inicial=(
                "¿Qué nivel de mantenimiento prefieres?\n"
                "*(bajo — poco arreglo | medio — algo de producto | alto — arreglo constante)*"
            ),
            pregunta_reintento="Escribe **bajo**, **medio** o **alto**.",
            pregunta_post_ayuda="¿Cuál de esos niveles se adapta mejor a tu rutina?",
            validos=_MANT_VALIDOS_SET,
            mensaje_ayuda=(
                "- **bajo** → te lavas el pelo y listo, sin productos\n"
                "- **medio** → usas algo de gel o cera de vez en cuando\n"
                "- **alto** → te arreglas el cabello todos los días\n\n"
                "¿Cuál es tu caso?"
            ),
        )
        if mant_texto is None:
            return

    nivel_float = _parsear_mantenimiento(mant_texto) or 0.5

    #  4. Motor difuso
    cortes = experto.recomendar_cortes(rostro, cabello, nivel_float)

    if not cortes:
        resp = (
            "No encontré cortes con buena compatibilidad para esa combinación.\n"
            "Escribe *'quiero una recomendación'* para intentarlo de nuevo."
        )
        _recordar("bot", resp)
        await cl.Message(content=resp).send()
        return

    etiqueta_mant = _ETIQ_MANT.get(nivel_float, "medio")
    resp = (
        f"Con rostro **{rostro}**, cabello **{cabello}** "
        f"y mantenimiento **{etiqueta_mant}**, el motor difuso recomienda:\n\n"
    )
    for c in cortes[:5]:
        resp += (
            f"**{c['corte']}** — {c['puntuacion']}/100\n"
            f"Rostro {c['compat_rostro']}% · Cabello {c['compat_cabello']}% · "
            f"Mantenimiento {c['mantenimiento']}\n"
            f"*{c['descripcion']}*\n\n"
        )
    resp += "Escribe el nombre del corte que te gustó para agendar tu cita."

    _recordar("bot", resp)
    cl.user_session.set("estado", "esperando_eleccion_corte")
    await cl.Message(content=resp).send()