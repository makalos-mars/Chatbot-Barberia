
from datetime import datetime, timedelta

DURACION = 30   # minutos por cita

# Configuración explícita por día
BARBEROS_CONFIG: dict = {
    "MAU": {
        "dias_libre": ["Domingo", "Miércoles"],
        "turnos": {
            "Lunes":     {"entrada": "09:00", "salida": "20:00", "comida": ("13:00", "15:00")},
            "Martes":    {"entrada": "09:00", "salida": "20:00", "comida": ("13:00", "15:00")},
            "Jueves":    {"entrada": "09:00", "salida": "20:00", "comida": ("13:00", "15:00")},
            "Viernes":   {"entrada": "09:00", "salida": "20:00", "comida": ("13:00", "15:00")},
            "Sábado":    {"entrada": "09:00", "salida": "20:00", "comida": ("13:00", "15:00")},
        },
    },
    "TONY": {
        "dias_libre": ["Domingo", "Jueves"],
        "turnos": {
            "Lunes":     {"entrada": "09:00", "salida": "19:00", "comida": ("12:00", "14:00")},
            "Martes":    {"entrada": "10:00", "salida": "20:00", "comida": ("14:00", "16:00")},
            "Miércoles": {"entrada": "09:00", "salida": "20:00", "comida": ("13:00", "15:00")},
            "Viernes":   {"entrada": "10:00", "salida": "20:00", "comida": ("14:00", "16:00")},
            "Sábado":    {"entrada": "09:00", "salida": "19:00", "comida": ("12:00", "14:00")},
        },
    },
    "RIATANA": {
        "dias_libre": ["Domingo", "Viernes"],
        "turnos": {
            "Lunes":     {"entrada": "11:00", "salida": "20:00", "comida": ("15:00", "17:00")},
            "Martes":    {"entrada": "09:00", "salida": "18:00", "comida": ("12:00", "14:00")},
            "Miércoles": {"entrada": "10:00", "salida": "20:00", "comida": ("14:00", "16:00")},
            "Jueves":    {"entrada": "10:00", "salida": "20:00", "comida": ("14:00", "16:00")},
            "Sábado":    {"entrada": "11:00", "salida": "20:00", "comida": ("15:00", "17:00")},
        },
    },
    "YAHIR": {
        "dias_libre": ["Domingo", "Martes"],
        "turnos": {
            "Lunes":     {"entrada": "10:00", "salida": "20:00", "comida": ("14:00", "16:00")},
            "Miércoles": {"entrada": "09:00", "salida": "18:00", "comida": ("12:00", "14:00")},
            "Jueves":    {"entrada": "09:00", "salida": "18:00", "comida": ("12:00", "14:00")},
            "Viernes":   {"entrada": "09:00", "salida": "18:00", "comida": ("12:00", "14:00")},
            "Sábado":    {"entrada": "10:00", "salida": "20:00", "comida": ("14:00", "16:00")},
        },
    },
}

_DIAS_MAP = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo",
}

# Base de datos en memoria
CITAS_RESERVADAS: dict[str, dict[str, list[str]]] = {}


# Utilidades
def _t(s: str) -> datetime:
    return datetime.strptime(s, "%H:%M")


def _slots_globales() -> list[str]:
    slots, t = [], _t("09:00")
    while t + timedelta(minutes=DURACION) <= _t("20:00"):
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=DURACION)
    return slots


_SLOTS = _slots_globales()   # ["09:00", "09:30", … , "19:30"]


# Clase CSP
class BarberiaCSP:

    def __init__(self, fecha_str: str, barbero_forzado: str | None = None):
        self.fecha = fecha_str
        dia_ingles = datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%A")
        self.dia = _DIAS_MAP[dia_ingles]

        candidatos = [barbero_forzado] if barbero_forzado else list(BARBEROS_CONFIG.keys())
        self.dominios: dict[str, list] = {
            "barbero": candidatos,
            "hora":    list(_SLOTS),
        }
        # Guarda valores podados por Forward Checking para poder restaurarlos
        self._podas: dict[str, dict[str, list]] = {}

    # Restricciones

    def _c1_trabaja(self, b: str) -> bool:
        cfg = BARBEROS_CONFIG[b]
        return self.dia not in cfg["dias_libre"] and self.dia in cfg["turnos"]

    def _c2_en_turno(self, b: str, h: str) -> bool:
        turno = BARBEROS_CONFIG[b]["turnos"].get(self.dia)
        if not turno:
            return False
        fin_cita = _t(h) + timedelta(minutes=DURACION)
        return _t(turno["entrada"]) <= _t(h) and fin_cita <= _t(turno["salida"])

    def _c3_fuera_comida(self, b: str, h: str) -> bool:
        c_ini, c_fin = BARBEROS_CONFIG[b]["turnos"][self.dia]["comida"]
        return not (_t(c_ini) <= _t(h) < _t(c_fin))

    def _c4_libre(self, b: str, h: str) -> bool:
        return h not in CITAS_RESERVADAS.get(self.fecha, {}).get(b, [])

    def _consistente(self, var: str, valor: str, asig: dict) -> bool:

        temp = {**asig, var: valor}
        b = temp.get("barbero")
        h = temp.get("hora")

        if b and not self._c1_trabaja(b):
            return False
        if b and h:
            if not self._c2_en_turno(b, h):
                return False
            if not self._c3_fuera_comida(b, h):
                return False
            if not self._c4_libre(b, h):
                return False
        return True

    # Heurística MRV

    def _mrv(self, libres: list[str], asig: dict) -> str:
        return min(
            libres,
            key=lambda v: sum(
                1 for val in self.dominios[v]
                if self._consistente(v, val, asig)
            ),
        )

    # Forward Checking
    def _forward_check(self, var: str, asig: dict) -> bool:
        self._podas[var] = {}
        for otra in self.dominios:
            if otra in asig:
                continue
            validos, eliminados = [], []
            for val in self.dominios[otra]:
                if self._consistente(otra, val, asig):
                    validos.append(val)
                else:
                    eliminados.append(val)
            if eliminados:
                self._podas[var][otra] = eliminados
                self.dominios[otra] = validos
            if not self.dominios[otra]:
                return False
        return True

    def _restaurar(self, var: str) -> None:
        """Devuelve al dominio los valores que se podaron al asignar `var`."""
        for otra, vals in self._podas.pop(var, {}).items():
            self.dominios[otra].extend(vals)

    # Motor de búsqueda

    def backtrack(self, asig: dict | None = None) -> dict | None:
        if asig is None:
            asig = {}
        if set(asig) == set(self.dominios):
            return asig                              #  solución encontrada

        libres = [v for v in self.dominios if v not in asig]
        var = self._mrv(libres, asig)

        for valor in list(self.dominios[var]):
            if self._consistente(var, valor, asig):
                asig[var] = valor
                if self._forward_check(var, asig):   # poda anticipada
                    resultado = self.backtrack(asig)
                    if resultado:
                        return resultado
                del asig[var]
                self._restaurar(var)                 # ← retroceso real

        return None

    def buscar_todos(self, limite: int = 40) -> list[dict]:
        soluciones: list[dict] = []
        orden = ["barbero", "hora"]

        def _explorar(asig: dict, idx: int) -> None:
            if len(soluciones) >= limite:
                return
            if idx == len(orden):
                soluciones.append(dict(asig))
                return
            var = orden[idx]
            for val in self.dominios[var]:
                if self._consistente(var, val, asig):
                    asig[var] = val
                    _explorar(asig, idx + 1)
                    del asig[var]

        _explorar({}, 0)
        return soluciones


def buscar_disponibilidad(fecha: str, barbero: str | None = None) -> list[dict]:
    return BarberiaCSP(fecha, barbero_forzado=barbero).buscar_todos()


def agendar_cita(fecha: str, hora: str, barbero: str) -> tuple[bool, str]:
    csp = BarberiaCSP(fecha, barbero_forzado=barbero)
    asig_parcial = {"barbero": barbero}

    if not csp._consistente("hora", hora, asig_parcial):
        libres = sorted({s["hora"] for s in csp.buscar_todos()})
        txt = ", ".join(libres) if libres else "ninguno disponible"
        return False, f"El horario {hora} no está libre para {barbero}.\nOpciones: {txt}"

    CITAS_RESERVADAS.setdefault(fecha, {b: [] for b in BARBEROS_CONFIG})
    CITAS_RESERVADAS[fecha][barbero].append(hora)
    return True, f"¡Cita confirmada! {barbero} te atiende el {fecha} a las {hora}."