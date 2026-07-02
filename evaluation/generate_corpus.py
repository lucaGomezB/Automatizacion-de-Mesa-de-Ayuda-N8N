"""
Generador de corpus simulado de 200 casos para evaluacion del clasificador hibrido.

Distribucion estratificada segun tesis (Capitulo 4, Seccion 4.4):
    - Sistemas: 82 casos (41%)
    - Operaciones: 64 casos (32%)
    - Soporte Tecnico: 54 casos (27%)

Uso:
    python evaluation/generate_corpus.py

Output:
    evaluation/data/corpus_evaluacion.csv  (200 filas + cabecera)

ADVERTENCIA: DATOS SIMULADOS. NO contiene PII real. Usa placeholders genericos.
Este corpus NO debe usarse para reportar metricas en la tesis (Capitulo 7).
"""

from __future__ import annotations

import csv
import pathlib
import random
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Configuracion global
# ---------------------------------------------------------------------------
SEED = 42
OUTPUT_DIR = pathlib.Path(__file__).parent / "data"
OUTPUT_PATH = OUTPUT_DIR / "corpus_evaluacion.csv"

# ---------------------------------------------------------------------------
# Placeholders — valores genericos, sin PII real
# ---------------------------------------------------------------------------
SERVIDORES: list[str] = [
    "SRV-APP-01", "SRV-APP-02", "SRV-BBDD-01", "SRV-FILE-01",
    "SRV-WEB-01", "srv-dominio", "SRV-PROXY", "SRV-BACKUP",
    "srv-bbdd-02", "SRV-ERP", "SRV-VPN", "srv-correo",
]

SISTEMAS_NOMBRES: list[str] = [
    "el sistema de gestion", "SAP", "Tango", "el ERP",
    "el sistema de facturacion", "el CRM", "Active Directory",
    "el sistema de turnos", "el portal interno", "el sistema de compras",
    "el modulo de RRHH", "el sistema contable", "GDE",
]

PERSONAS: list[str] = [
    "Juan Perez", "Maria Garcia", "Carlos Lopez", "Ana Martinez",
    "Pedro Rodriguez", "Laura Fernandez", "Diego Gonzalez", "Sofia Diaz",
    "Martin Sanchez", "Valentina Torres", "Pablo Ramirez", "Carla Flores",
]

EMAILS: list[str] = [
    "juan.perez@empresa.com.ar",
    "maria.garcia@empresa.com.ar",
    "carlos.lopez@empresa.com.ar",
    "ana.martinez@empresa.com.ar",
]

TELEFONOS: list[str] = [
    "+54 261 555-0101", "+54 261 555-0102", "+54 261 555-0103",
    "+54 261 555-0104", "+54 261 555-0105",
]

AREAS: list[str] = [
    "Contabilidad", "RRHH", "Compras", "Ventas", "Marketing",
    "Legales", "Gerencia", "Logistica", "Administracion", "Sistemas",
]

PISOS: list[str] = ["piso 1", "piso 2", "piso 3", "planta baja", "piso 4"]

IMPRESORAS: list[str] = [
    "la impresora del area", "la multifuncion HP", "la impresora de red",
    "la fotocopiadora", "la impresora del piso 2",
]

APLICACIONES: list[str] = [
    "el navegador", "Excel", "Word", "Outlook", "el cliente de correo",
    "Chrome", "Firefox", "el antivirus", "la VPN",
]

# ---------------------------------------------------------------------------
# Templates por categoria
# ---------------------------------------------------------------------------

# --- Sistemas (82 casos) ---
SISTEMAS_TEMPLATES: list[str] = [
    # Servidores caidos / no responden
    "No puedo acceder al servidor {server}. Me tira error de conexion desde hace {horas} horas.",
    "El servidor {server} no responde. Todo el equipo de {area} esta parado.",
    "Se cayo {server} y no podemos laburar. Es urgente, tenemos cierre hoy.",
    "El {server} esta dando timeout. Ya reiniciamos dos veces y sigue igual.",
    "Buenos dias. El servidor {server} presenta problemas de conectividad desde temprano. Solicito revision urgente.",
    "Hace {horas} horas que {server} no responde. Nadie del area {area} puede ingresar al sistema.",
    # Red / conectividad
    "No tengo internet en mi puesto. Aparentemente todo el {piso} esta igual.",
    "La red del {piso} esta caida. Los equipos no tienen conectividad.",
    "Problemas de red en {piso}. No hay acceso a internet ni a los servidores internos.",
    "WiFi caido en {piso}. Urgente porque tenemos reunion por videollamada en 15 minutos.",
    "El {piso} se quedo sin red. Avisen cuando vuelva porque tenemos entregas pendientes.",
    "Hay mucha lentitud en la red. Las paginas tardan una eternidad en cargar.",
    "Che, no anda internet en {piso}. Me fije los cables y estan bien, pero no conecta.",
    "La conexion a internet esta intermitente desde ayer. A veces anda, a veces no.",
    # VPN
    "No me puedo conectar a la VPN desde casa. Me tira error de autenticacion.",
    "La VPN no me deja entrar. Probe desde dos equipos distintos y nada.",
    "VPN caida. Todo el equipo remoto no puede acceder a los servidores.",
    "Buenas, estoy de home office y la VPN no conecta. Error 809. Es urgente.",
    "VPN no funciona. Ya reinstale el cliente y sigue igual. Necesito acceso remoto para terminar un informe.",
    # Base de datos
    "La base de datos esta lenta. Las consultas demoran mucho mas de lo normal.",
    "Error de conexion a la base de datos en {sistema}. No puedo cargar los datos del cierre.",
    "El {sistema} tira error 500. Parece que la base de datos no responde.",
    "No puedo hacer consultas en {sistema}. La base de datos devuelve timeout.",
    "La base de datos de produccion esta saturada. Las consultas tardan 10 veces mas.",
    # Permisos / acceso
    "Necesito permisos de administrador en {sistema}. No puedo aprobar las solicitudes pendientes.",
    "No tengo acceso a la carpeta compartida de {area}. Me aparece acceso denegado.",
    "El usuario {persona} no puede acceder a {sistema}. Pide permisos de lectura.",
    "Buenas. Solicito acceso al modulo de {sistema} para el equipo de {area}. Somos 4 personas.",
    "Me bloquearon el acceso a la carpeta de red. Necesito que me restauren los permisos.",
    "No puedo acceder a los archivos compartidos del servidor. Error de permisos.",
    # Instalacion de software / actualizaciones
    "Necesito instalar {app} en mi PC. No tengo permisos de administrador.",
    "La actualizacion de {sistema} fallo. Ahora el sistema no abre.",
    "Despues de la actualizacion de ayer, {app} dejo de funcionar. Se cierra solo.",
    "Hay que actualizar {sistema} en todas las PCs de {area}. Ya esta el instalador.",
    "Instale una actualizacion de Windows y ahora no me anda {app}.",
    "No puedo instalar el software de gestion. Me pide permisos que no tengo.",
    "Actualizacion de {sistema} pendiente. No puedo trabajar hasta que se complete.",
    # Errores de sistema
    "El {sistema} esta caido desde las {horas} AM. No podemos facturar.",
    "{sistema} da error al iniciar sesion. Pantalla en blanco despues del login.",
    "Se colgo {sistema}. No responde a nada. Intente cerrar y abrir y sigue igual.",
    "El proceso batch de {sistema} no se ejecuto anoche. Hay que correrlo manual.",
    "Error 403 en {sistema}. No me deja entrar con mi usuario de siempre.",
    "El modulo de reportes de {sistema} no genera PDF. Da error de renderizado.",
]

# --- Operaciones (64 casos) ---
OPERACIONES_TEMPLATES: list[str] = [
    # Bloqueo de cuenta / login
    "Me bloquearon la cuenta. Intente entrar tres veces y ahora no me deja.",
    "No puedo iniciar sesion en {sistema}. Dice usuario bloqueado. Necesito desbloqueo urgente.",
    "Buenas, {persona} tiene la cuenta bloqueada en {sistema}. Hicimos varios intentos fallidos.",
    "Cuenta bloqueada por intentos fallidos. Por favor desbloqueen al usuario {persona}.",
    "No puedo entrar a la red. Cambie la clave ayer y ahora no me la toma.",
    "Al iniciar sesion me dice 'cuenta deshabilitada'. Necesito acceso hoy.",
    # Reseteo de clave / password
    "Olvide mi contrasena de {sistema}. Necesito resetearla urgente.",
    "Nesecito cambiar la clave de {sistema}. Me olvide la anterior.",
    "La contrasena de {sistema} expiro. No me deja poner una nueva.",
    "{persona} no recuerda su clave de acceso. Solicita reseteo urgente.",
    "Buenos dias, necesito un reseteo de clave para {sistema}. Mi usuario es {email}.",
    "Me olvide la contrase�a del sistema. No puedo ingresar a {sistema}.",
    "Hay que resetear la clave de {persona}. Ya cumplio el plazo de vencimiento.",
    # Alta / baja de empleados
    "Ingreso {persona} al area {area} hoy. Necesita usuario, mail y acceso a {sistema}.",
    "Alta de nuevo empleado: {persona} en {area}. Necesita todo el setup de sistemas.",
    "Por favor den de alta a {persona} en el sistema. Empieza manana en {area}.",
    "Baja de {persona} del area {area}. Hay que deshabilitar todos sus accesos.",
    "{persona} se desvinculo de la empresa. Bloquear accesos a todos los sistemas.",
    "Dar de baja usuario {email}. Ya no trabaja en la empresa. Urgente por seguridad.",
    # Solicitudes de acceso
    "El equipo de {area} necesita acceso al modulo de reportes de {sistema}.",
    "Solicito acceso a {sistema} para {persona}. Es nuevo en el area {area}.",
    "Buenos dias. Necesito permisos de edicion en la carpeta compartida de {area}.",
    "{persona} necesita acceso temporal a {sistema} por cobertura de vacaciones.",
    "Solicitud de acceso a {sistema} para pasante de {area} por 3 meses.",
    # Procesos operativos / formularios
    "El sistema de pedidos no me deja cargar una solicitud nueva. Error al guardar.",
    "No puedo aprobar solicitudes en {sistema}. El boton de aprobar no aparece.",
    "El proceso de cierre de {area} no se ejecuto. Hay que revisar los logs.",
    "Error al generar el reporte mensual de {area}. Faltan datos de la semana pasada.",
    "El formulario de carga de {sistema} no valida los campos correctamente.",
    "No se generaron las notificaciones automaticas de {sistema} este mes.",
    "El workflow de aprobacion de {area} esta trabado. Quedo en bandeja de {persona}.",
    "Error en el proceso batch de facturacion. No proceso los archivos de anoche.",
    "El modulo de {area} en {sistema} no refleja los cambios que hice ayer.",
    "No puedo dar de alta un proveedor en {sistema}. Da error de duplicado.",
    "El sistema de turnos no asigna correctamente los horarios esta semana.",
    "Perdi todos los datos que cargue en {sistema}. Se cerro la sesion sin guardar.",
    # Problemas de sincronizacion
    "Los datos entre {sistema} y SAP no se sincronizan desde ayer.",
    "La replica de datos entre servidores no se completo. Faltan registros.",
    "No me aparecen los registros que cargue ayer en {sistema}. Se perdieron?",
    "La sincronizacion de {sistema} con Active Directory fallo. Usuarios nuevos no pueden entrar.",
]

# --- Soporte Tecnico (54 casos) ---
SOPORTE_TECNICO_TEMPLATES: list[str] = [
    # Impresoras
    "La impresora del sector no imprime. Le mande tres trabajos y no sale nada.",
    "{impresora} esta con luz roja titilando. No responde a nada.",
    "Necesito cambiar el toner de {impresora}. Ya esta pidiendo cambio.",
    "La impresora imprime todo borroso. Creo que necesita mantenimiento.",
    "{impresora} se atasca el papel todo el tiempo. Hay que revisarla urgente.",
    "No puedo instalar la impresora en mi PC. No aparece en la red.",
    "La impresora esta fuera de linea. No la encuentra ningun equipo del area.",
    "Sale una raya negra en todas las hojas que imprime {impresora}.",
    # PC / hardware
    "Mi PC no enciende. Aprieto el boton y no hace nada.",
    "La computadora de {persona} esta muy lenta. Tarda 10 minutos en arrancar.",
    "La PC se apaga sola cada 20 minutos. Calienta mucho la parte de atras.",
    "La pantalla se quedo en negro. La PC esta prendida pero no da video.",
    "El equipo de {persona} hace un ruido raro, como un ventilador roto.",
    "Mi computadora tira pantalla azul todas las mananas al arrancar.",
    "La PC no reconoce el disco externo. Necesito pasar unos archivos urgente.",
    "Sin querer tire cafe en el teclado de mi PC. No funciona ninguna tecla.",
    "La PC de {area} esta muy lenta. Necesita upgrade de memoria urgente.",
    "El puerto USB del frente no funciona. Probe con dos pendrives distintos.",
    # Monitor / pantalla
    "El monitor titila constantemente. Me esta haciendo doler los ojos.",
    "Se me rompio la pantalla. Aparecio una linea vertical de color verde.",
    "El monitor no enciende. La luz de power esta apagada completamente.",
    "La segunda pantalla no la detecta la PC. Ya probe cambiando el cable.",
    "Necesito un monitor adicional para {persona} en {area}. Estamos con una sola pantalla.",
    "La resolucion de la pantalla cambio sola y no la puedo volver a configurar.",
    # Teclado / mouse / perifericos
    "El mouse no funciona. Cambie las pilas y sigue igual.",
    "El teclado no escribe la letra 'a'. Hay que cambiarlo urgente porque no puedo trabajar.",
    "Se me rompio el mouse. Necesito uno nuevo para el puesto de {area}.",
    "El teclado de {persona} tiene varias teclas trabadas. Ya lo limpiamos y sigue igual.",
    "Necesito un hub USB. Mi notebook tiene un solo puerto y necesito conectar varias cosas.",
    "Los auriculares con microfono no me funcionan. Tengo reunion por Teams en 10 minutos.",
    # Telefonia
    "El telefono de mi puesto no funciona. No da tono.",
    "No puedo hacer llamadas externas desde el interno {telefono}.",
    "El telefono IP se reinicia solo. Pierdo las llamadas en el medio.",
    "Necesito un telefono nuevo para el puesto de {persona} en {area}.",
    "Las llamadas entrantes no se derivan correctamente al area {area}.",
    "El microfono del telefono no funciona. Me escuchan entrecortado.",
    # Cableado / infraestructura fisica
    "El cable de red de mi puesto esta roto. Se desconecta todo el tiempo.",
    "Hay un cable suelto en {piso} que deja sin conexion a varios puestos.",
    "El estabilizador de {area} hace un ruido electrico raro. Miedo a que se queme algo.",
    "Necesito un alargue con mas enchufes en mi puesto. Solo tengo uno.",
    "La ficha del monitor esta doblada. Hay que cambiarla antes que haga cortocircuito.",
    "Se corto un cable del rack de {piso}. Nadie en esa ala tiene conexion.",
    # Problemas de software en el puesto
    "Se me desinstalo {app} solo. Ayer funcionaba bien y hoy no esta.",
    "{app} se cierra inesperadamente cada vez que intento imprimir.",
    "El sistema operativo tarda una eternidad en iniciar. Mas de 15 minutos.",
    "No me deja abrir archivos PDF. Dice que no hay programa asociado.",
    "El calendario de Outlook no sincroniza con el telefono de {persona}.",
]

# ---------------------------------------------------------------------------
# Funciones de transformacion de realismo
# ---------------------------------------------------------------------------

ERRORES_TIPEO: Dict[str, str] = {
    "necesito": "nesecito",
    "conexion": "conecsion",
    "ayuda": "hayuda",
    "problema": "problema",
    "urgente": "urgente",
    "impresora": "impresora",
    "teclado": "tecaldo",
    "servidor": "servidor",
    "instalar": "instalar",
    "pantalla": "pantalla",
    "acceso": "acseso",
    "bloqueo": "bloqueo",
    "contrasena": "contrase\u00f1a",
    "sesion": "secion",
    "actualizacion": "actualisacion",
    "reinicio": "reinisio",
}


def _aplicar_errores_tip(descripcion: str, rng: random.Random, probabilidad: float = 0.10) -> str:
    """Aplica errores de tipeo aleatorios a ~10% de las descripciones."""
    if rng.random() < probabilidad:
        for correcta, incorrecta in ERRORES_TIPEO.items():
            if correcta in descripcion and rng.random() < 0.5:
                descripcion = descripcion.replace(correcta, incorrecta, 1)
                break  # solo un error por descripcion
    return descripcion


def _omitir_tildes_aleatorio(descripcion: str, rng: random.Random, probabilidad: float = 0.08) -> str:
    """Omite tildes en ~8% de las descripciones para simular escritura apurada."""
    if rng.random() < probabilidad:
        reemplazos = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u",
                        "A": "A", "E": "E", "I": "I", "O": "O", "U": "U"}
        for con_tilde, sin_tilde in reemplazos.items():
            descripcion = descripcion.replace(con_tilde, sin_tilde)
    return descripcion


# ---------------------------------------------------------------------------
# Funcion principal de generacion (testeable, pura)
# ---------------------------------------------------------------------------

def _generar_casos(seed: int = SEED) -> List[Dict[str, str]]:
    """
    Genera los 200 casos del corpus con distribucion estratificada.

    Args:
        seed: Semilla aleatoria para reproducibilidad.

    Returns:
        Lista de diccionarios con claves: id, descripcion, canal_origen, categoria_real.
        Los ids son strings y estan en orden secuencial 1..200.
    """
    rng = random.Random(seed)
    casos: List[Dict[str, str]] = []

    def _rellenar(template: str) -> str:
        """Rellena placeholders en un template con valores aleatorios."""
        return template.format(
            server=rng.choice(SERVIDORES),
            sistema=rng.choice(SISTEMAS_NOMBRES),
            persona=rng.choice(PERSONAS),
            email=rng.choice(EMAILS),
            telefono=rng.choice(TELEFONOS),
            area=rng.choice(AREAS),
            piso=rng.choice(PISOS),
            horas=rng.choice(["2", "3", "4", "5", "6"]),
            impresora=rng.choice(IMPRESORAS),
            app=rng.choice(APLICACIONES),
        )

    def _generar_para_categoria(
        templates: list[str], categoria: str, cantidad: int
    ) -> List[Dict[str, str]]:
        """Genera N casos para una categoria usando templates aleatorios."""
        resultado: List[Dict[str, str]] = []
        for _ in range(cantidad):
            template = rng.choice(templates)
            descripcion = _rellenar(template)
            descripcion = _aplicar_errores_tip(descripcion, rng, probabilidad=0.10)
            descripcion = _omitir_tildes_aleatorio(descripcion, rng, probabilidad=0.08)

            canal = rng.choices(
                ["correo", "formulario", "telefono"],
                weights=[60, 25, 15],
                k=1,
            )[0]

            resultado.append({
                "descripcion": descripcion,
                "canal_origen": canal,
                "categoria_real": categoria,
            })
        return resultado

    # Generar por categoria
    casos += _generar_para_categoria(SISTEMAS_TEMPLATES, "Sistemas", 82)
    casos += _generar_para_categoria(OPERACIONES_TEMPLATES, "Operaciones", 64)
    casos += _generar_para_categoria(SOPORTE_TECNICO_TEMPLATES, "Soporte Técnico", 54)

    # Mezclar para que no queden agrupados por categoria
    rng.shuffle(casos)

    # Asignar ids secuenciales
    for i, caso in enumerate(casos, start=1):
        caso["id"] = str(i)

    return casos


# ---------------------------------------------------------------------------
# Escritura del CSV
# ---------------------------------------------------------------------------

def _escribir_csv(casos: List[Dict[str, str]], output_path: pathlib.Path) -> None:
    """Escribe los casos generados a un archivo CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "descripcion", "canal_origen", "categoria_real"],
        )
        writer.writeheader()
        for caso in casos:
            writer.writerow({
                "id": caso["id"],
                "descripcion": caso["descripcion"],
                "canal_origen": caso["canal_origen"],
                "categoria_real": caso["categoria_real"],
            })


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Genera el corpus simulado y lo escribe en evaluation/data/."""
    casos = _generar_casos(seed=SEED)
    _escribir_csv(casos, OUTPUT_PATH)

    # Reporte de distribucion
    conteo: Dict[str, int] = {}
    for c in casos:
        conteo[c["categoria_real"]] = conteo.get(c["categoria_real"], 0) + 1

    print(f"Corpus simulado generado: {OUTPUT_PATH}")
    print(f"Total de casos: {len(casos)}")
    for categoria in sorted(conteo.keys()):
        print(f"  {categoria}: {conteo[categoria]}")
    print("ADVERTENCIA: Datos simulados. NO usar para metricas de tesis (Capitulo 7).")


if __name__ == "__main__":
    main()
