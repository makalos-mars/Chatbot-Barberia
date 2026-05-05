import chainlit as cl
import experto
import nlp
import agenda
import re

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def parsear_fecha(texto):
    """Convierte texto del usuario a formato YYYY-MM-DD."""
    from datetime import datetime, timedelta
    texto = texto.lower().strip()
    hoy = datetime.today()

    dias_map = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }

    for nombre_dia, num in dias_map.items():
        if nombre_dia in texto:
            dias_hasta = (num - hoy.weekday()) % 7
            if dias_hasta == 0:
                dias_hasta = 7
            fecha = hoy + timedelta(days=dias_hasta)
            return fecha.strftime("%Y-%m-%d")

    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
        "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9,
        "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    for nombre_mes, num_mes in meses.items():
        if nombre_mes in texto:
            try:
                dia_num = int("".join(filter(str.isdigit, texto)))
                from datetime import datetime
                fecha = datetime(hoy.year, num_mes, dia_num)
                return fecha.strftime("%Y-%m-%d")
            except:
                pass

    return None


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("estado", None)
    cl.user_session.set("nombre", None)
    cl.user_session.set("barbero", None)
    cl.user_session.set("fecha", None)
    cl.user_session.set("hora", None)
    cl.user_session.set("corte_elegido", None)
    await cl.Message(
        content=(
            "¡Bienvenido a la barbería! ¿En qué te puedo ayudar hoy?\n\n"
            "Puedes decirme cosas como:\n"
            "- *'Quiero agendar una cita'*\n"
            "- *'Quiero una recomendación de corte'*"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    texto = message.content.strip()
    estado = cl.user_session.get("estado")

    # --- ESTADO: conversación finalizada, volver al menú ---
    if estado == "finalizado":
        cl.user_session.set("estado", None)
        await cl.Message(
            content=(
                "¿Hay algo más en lo que pueda ayudarte?\n\n"
                "- *'Quiero agendar una cita'*\n"
                "- *'Quiero una recomendación de corte'*"
            )
        ).send()
        return

    # --- ESTADO: esperando elección de corte ---
    if estado == "esperando_eleccion_corte":
        cl.user_session.set("corte_elegido", texto)
        cl.user_session.set("estado", "esperando_nombre")
        await cl.Message(
            content=f"¡Excelente elección! Ahora agendemos tu cita.\n¿Cuál es tu nombre?"
        ).send()
        return

    # --- ESTADO: esperando nombre ---
    if estado == "esperando_nombre":
        cl.user_session.set("nombre", texto)
        cl.user_session.set("estado", "esperando_preferencia_barbero")
        await cl.Message(
            content=f"Perfecto, {texto}. ¿Tienes preferencia de barbero o te atendemos con cualquiera?\n\n"
                    f"Nuestros barberos son: **{'**, **'.join(agenda.BARBEROS.keys())}**"
        ).send()
        return

    # --- ESTADO: esperando preferencia de barbero ---
    if estado == "esperando_preferencia_barbero":
        texto_lower = texto.lower()
        barbero_encontrado = None

        for nombre_barbero in agenda.BARBEROS:
            if nombre_barbero.lower() in texto_lower:
                barbero_encontrado = nombre_barbero
                break

        if barbero_encontrado:
            cl.user_session.set("barbero", barbero_encontrado)
            cl.user_session.set("estado", "esperando_fecha")
            await cl.Message(
                content=f"¡Perfecto, con **{barbero_encontrado}**! ¿Qué día te gustaría venir?\n"
                        f"(ej: lunes, martes, 10 de junio...)"
            ).send()
        else:
            cl.user_session.set("barbero", None)
            cl.user_session.set("estado", "esperando_fecha")
            await cl.Message(
                content="¡Sin problema! ¿Qué día te gustaría venir?\n"
                        "(ej: lunes, martes, 10 de junio...)"
            ).send()
        return

    # --- ESTADO: esperando fecha ---
    if estado == "esperando_fecha":
        fecha_str = parsear_fecha(texto)

        if not fecha_str:
            await cl.Message(
                content="No entendí la fecha. Intenta con algo como *'lunes'*, *'viernes'* o *'10 de junio'*."
            ).send()
            return

        cl.user_session.set("fecha", fecha_str)
        barbero = cl.user_session.get("barbero")

        if barbero:
            bloques = agenda.generar_bloques_disponibles(barbero, fecha_str)
            if bloques:
                horarios = ", ".join(bloques)
                cl.user_session.set("estado", "esperando_hora")
                await cl.Message(
                    content=f"**{barbero}** tiene disponibles estos horarios para ese día:\n\n{horarios}\n\n¿Cuál te viene mejor?"
                ).send()
            else:
                await cl.Message(
                    content=f"**{barbero}** no tiene disponibilidad ese día. ¿Quieres intentar con otro día?"
                ).send()
        else:
            horarios_disponibles = set()
            for nombre_barbero in agenda.BARBEROS:
                bloques = agenda.generar_bloques_disponibles(nombre_barbero, fecha_str)
                horarios_disponibles.update(bloques)

            if horarios_disponibles:
                horarios_ordenados = sorted(horarios_disponibles)
                cl.user_session.set("estado", "esperando_hora_cualquiera")
                await cl.Message(
                    content=f"Estos son los horarios disponibles para ese día:\n\n"
                            f"{', '.join(horarios_ordenados)}\n\n"
                            f"¿Cuál te viene mejor?"
                ).send()
            else:
                await cl.Message(
                    content="No hay disponibilidad ese día. ¿Quieres intentar con otro día?"
                ).send()
        return

    # --- ESTADO: esperando hora (cuando eligió cualquier barbero) ---
    if estado == "esperando_hora_cualquiera":
        match = re.search(r'\b(\d{1,2}:\d{2})\b', texto)
        hora_elegida = match.group(1).zfill(5) if match else texto.strip()

        fecha = cl.user_session.get("fecha")

        barbero_asignado = None
        for nombre_barbero in agenda.BARBEROS:
            bloques = agenda.generar_bloques_disponibles(nombre_barbero, fecha)
            if hora_elegida in bloques:
                barbero_asignado = nombre_barbero
                break

        if not barbero_asignado:
            await cl.Message(
                content="Ese horario no está disponible. Intenta con otra hora."
            ).send()
            return

        exito, msg = agenda.agendar_cita(fecha, hora_elegida, barbero_asignado)

        if exito:
            nombre = cl.user_session.get("nombre")
            corte = cl.user_session.get("corte_elegido")
            cl.user_session.set("estado", "finalizado")
            confirmacion = (
                f"¡Listo, {nombre}! Tu cita quedó agendada:\n\n"
                f"**Día:** {fecha}\n"
                f"**Hora:** {hora_elegida}\n"
            )
            if corte:
                confirmacion += f"**Corte:** {corte}\n"
            confirmacion += "\n¡Te esperamos!"
            await cl.Message(content=confirmacion).send()
        else:
            await cl.Message(content=f"{msg}\n\nIntenta con otro horario.").send()
        return

    # --- ESTADO: esperando hora (cuando ya eligió barbero específico) ---
    if estado == "esperando_hora":
        match = re.search(r'\b(\d{1,2}:\d{2})\b', texto)
        hora_elegida = match.group(1).zfill(5) if match else texto.strip()

        fecha = cl.user_session.get("fecha")
        barbero = cl.user_session.get("barbero")
        exito, msg = agenda.agendar_cita(fecha, hora_elegida, barbero)

        if exito:
            nombre = cl.user_session.get("nombre")
            corte = cl.user_session.get("corte_elegido")
            cl.user_session.set("estado", "finalizado")
            confirmacion = (
                f"¡Listo, {nombre}! Tu cita quedó agendada:\n\n"
                f"**Día:** {fecha}\n"
                f"**Hora:** {hora_elegida}\n"
                f"**Barbero:** {barbero}\n"
            )
            if corte:
                confirmacion += f"**Corte:** {corte}\n"
            confirmacion += "\n¡Te esperamos!"
            await cl.Message(content=confirmacion).send()
        else:
            bloques = agenda.generar_bloques_disponibles(barbero, fecha)
            horarios = ", ".join(bloques) if bloques else "ninguno"
            await cl.Message(
                content=f"{msg}\n\nLos horarios disponibles son: {horarios}"
            ).send()
        return

    # --- FLUJO NORMAL: clasificar intención ---
    intencion = nlp.clasificar_intencion(texto.lower())

    if intencion == "consejo":
        res_rostro = await cl.AskUserMessage(
            content="¿Qué forma tiene tu rostro? (ovalado, redondo, cuadrado, alargado, diamante, triangulo invertido, hexagonal)"
        ).send()
        if res_rostro:
            rostro = res_rostro["output"]
            res_cabello = await cl.AskUserMessage(
                content="¿Cómo es tu tipo de cabello? (liso, ondulado, rizado, afro)"
            ).send()
            if res_cabello:
                cabello = res_cabello["output"]
                cortes = experto.evaluar_cortes(rostro, cabello)
                if cortes:
                    respuesta = "Aquí tienes los cortes que mejor te quedan:\n\n"
                    for c in cortes:
                        respuesta += (
                            f"- **{c['corte']}** ({c['compatibilidad']}% compatible)\n"
                            f"  {c['descripcion']}\n\n"
                        )
                    respuesta += "Escribe el nombre del corte que te gustó para agendar tu cita."
                    cl.user_session.set("estado", "esperando_eleccion_corte")
                else:
                    respuesta = "No encontré un corte exacto. Intenta escribir las opciones tal cual se muestran."
                await cl.Message(content=respuesta).send()

    elif intencion == "agendar":
        cl.user_session.set("estado", "esperando_nombre")
        await cl.Message(content="¡Con gusto! ¿Cuál es tu nombre?").send()

    else:
        await cl.Message(
            content=(
                "No entendí bien tu mensaje. Puedes decirme:\n"
                "- *'Quiero agendar una cita'*\n"
                "- *'Quiero una recomendación de corte'*"
            )
        ).send()