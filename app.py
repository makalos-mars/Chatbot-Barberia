import chainlit as cl
import experto


@cl.on_message
async def on_message(message: cl.Message):
    texto = message.content.lower()

    # Por ahora usamos un if simple. Luego meteremos el NLP aquí.
    if "corte" in texto or "recomendacion" in texto or "recomendar" in texto:

        # Preguntamos por el rostro
        res_rostro = await cl.AskUserMessage(
            content="¿Qué forma tiene tu rostro? (ovalado, redondo, cuadrado, alargado, diamante, triangulo invertido, hexagonal)"
        ).send()

        if res_rostro:
            rostro = res_rostro['output']

            # Preguntamos por el cabello
            res_cabello = await cl.AskUserMessage(
                content="¿Cómo es tu tipo de cabello? (liso, ondulado, rizado, afro)"
            ).send()

            if res_cabello:
                cabello = res_cabello['output']

                # Llamamos al sistema experto
                cortes = experto.evaluar_cortes(rostro, cabello)

                if cortes:
                    respuesta = "Aquí tienes los cortes que mejor te quedan:\n\n"
                    for c in cortes:
                        respuesta += f"- **{c['corte']}** ({c['compatibilidad']}% compatible)\n  {c['descripcion']}\n\n"
                else:
                    respuesta = "No encontré un corte exacto, intenta escribiendo las opciones tal cual."

                await cl.Message(content=respuesta).send()

    else:
        await cl.Message(content="Hola. Escribe 'quiero una recomendacion' para ayudarte a elegir tu corte.").send()