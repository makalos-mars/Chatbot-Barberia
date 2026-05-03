# agenda.py

# Duración de cada cita en minutos
DURACION_CITA = 30

BARBEROS = {
    "MAU": {
        "dias_libre": ["Domingo", "Miércoles"],
        "horario_entrada": "09:00",
        "horario_salida": "20:00",
        "comida_inicio": "13:00",
        "comida_fin": "15:00"
    },
    "TONY": {
        "dias_libre": ["Domingo", "Jueves"],
        "horario_entrada_regular": "09:00", # L, M, Mi, S
        "horario_entrada_tarde": "10:00",   # Martes, Viernes
        "horario_salida_temprano": "19:00", # Lunes, Sábado
        "horario_salida_regular": "20:00",  # M, Mi, V
        "comida_inicio_1": "12:00", # L, S
        "comida_fin_1": "14:00",
        "comida_inicio_2": "13:00", # Mi
        "comida_fin_2": "15:00",
        "comida_inicio_3": "14:00", # M, V
        "comida_fin_3": "16:00"
        # Nota: La lógica de Tony varía por día, lo manejaremos en la función de generación de turnos
    },
    "RIATANA": {
        "dias_libre": ["Domingo", "Viernes"],
        "horario_entrada": "10:00", # Mi, J (L, S entra a las 11, M entra a las 9)
        "horario_salida": "20:00",  # L, Mi, J, S (M sale a las 18)
        "comida_inicio": "14:00",
        "comida_fin": "16:00"
    },
    "YAHIR": {
        "dias_libre": ["Domingo", "Martes"],
        "horario_entrada": "09:00", # Mi, J, V (L, S entra a las 10)
        "horario_salida": "18:00",  # Mi, J, V (L, S sale a las 20)
        "comida_inicio": "12:00",
        "comida_fin": "14:00"
    }
}