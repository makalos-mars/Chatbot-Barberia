from datetime import datetime, timedelta

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
    },
    "RIATANA": {
        "dias_libre": ["Domingo", "Viernes"],
        "horario_entrada": "10:00", # Estándar Mi, J
        "horario_salida": "20:00",  
        "comida_inicio": "14:00",
        "comida_fin": "16:00"
    },
    "YAHIR": {
        "dias_libre": ["Domingo", "Martes"],
        "horario_entrada": "09:00", # Estándar Mi, J, V
        "horario_salida": "18:00", 
        "comida_inicio": "12:00",
        "comida_fin": "14:00"
    }
}

# Diccionario Global para evitar empalmes (Base de datos temporal)
# Estructura: { '2026-05-05': { 'MAU': ['09:00'], 'TONY': [] } }
CITAS_RESERVADAS = {}

def obtener_config_dia(nombre_barbero, dia_esp):
    """Aplica la lógica matemática de horarios variables por día."""
    b = BARBEROS[nombre_barbero]
    config = {
        "entrada": b.get("horario_entrada", "09:00"),
        "salida": b.get("horario_salida", "20:00"),
        "c_ini": b.get("comida_inicio", "13:00"),
        "c_fin": b.get("comida_fin", "15:00")
    }

    # Lógica específica para TONY
    if nombre_barbero == "TONY":
        if dia_esp in ["Martes", "Viernes"]:
            config["entrada"] = b["horario_entrada_tarde"]
            config["c_ini"], config["c_fin"] = b["comida_inicio_3"], b["comida_fin_3"]
        if dia_esp in ["Lunes", "Sábado"]:
            config["salida"] = b["horario_salida_temprano"]
            config["c_ini"], config["c_fin"] = b["comida_inicio_1"], b["comida_fin_1"]
        if dia_esp == "Miércoles":
            config["c_ini"], config["c_fin"] = b["comida_inicio_2"], b["comida_fin_2"]

    # Lógica específica para RIATANA
    elif nombre_barbero == "RIATANA":
        if dia_esp in ["Lunes", "Sábado"]: config["entrada"] = "11:00"
        if dia_esp == "Martes": 
            config["entrada"], config["salida"] = "09:00", "18:00"

    # Lógica específica para YAHIR
    elif nombre_barbero == "YAHIR":
        if dia_esp in ["Lunes", "Sábado"]: 
            config["entrada"], config["salida"] = "10:00", "20:00"

    return config

def generar_bloques_disponibles(nombre_barbero, fecha_str):
    """Genera bloques de 30 min libres de un barbero (Satisfacción de Restricciones)."""
    if nombre_barbero not in BARBEROS: return []
    
    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
    dias_map = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", 
                "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    dia_esp = dias_map[fecha_obj.strftime("%A")]

    if dia_esp in BARBEROS[nombre_barbero]["dias_libre"]: return []

    cfg = obtener_config_dia(nombre_barbero, dia_esp)
    
    hora_act = datetime.strptime(cfg["entrada"], "%H:%M")
    hora_lim = datetime.strptime(cfg["salida"], "%H:%M")
    c_ini = datetime.strptime(cfg["c_ini"], "%H:%M")
    c_fin = datetime.strptime(cfg["c_fin"], "%H:%M")

    bloques = []
    while hora_act + timedelta(minutes=DURACION_CITA) <= hora_lim:
        if not (hora_act >= c_ini and hora_act < c_fin):
            # Verificar que no esté ya reservado en CITAS_RESERVADAS
            h_str = hora_act.strftime("%H:%M")
            reservadas = CITAS_RESERVADAS.get(fecha_str, {}).get(nombre_barbero, [])
            if h_str not in reservadas:
                bloques.append(h_str)
        hora_act += timedelta(minutes=DURACION_CITA)
    
    return bloques

def agendar_cita(fecha, hora, nombre_barbero):
    """Intenta asignar la cita validando todas las restricciones."""
    disponibles = generar_bloques_disponibles(nombre_barbero, fecha)
    
    if hora not in disponibles:
        return False, f"El horario {hora} no está disponible para {nombre_barbero}."

    if fecha not in CITAS_RESERVADAS:
        CITAS_RESERVADAS[fecha] = {b: [] for b in BARBEROS}
    
    CITAS_RESERVADAS[fecha][nombre_barbero].append(hora)
    return True, f"Cita confirmada con {nombre_barbero} el {fecha} a las {hora}."