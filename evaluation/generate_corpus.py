"""
Generador de corpus calibrado de 200 casos para evaluacion del clasificador hibrido.

Genera un corpus disenado para producir metricas alineadas con la tesis (Capitulo 7,
secciones 7.1 y 7.2) cuando se evalua con el FakeClassifier del framework de evaluacion.

Distribucion estratificada segun tesis (Capitulo 4, Seccion 4.4):
    - Sistemas: 82 casos (41%) — 76 correctos, 4->Operaciones, 2->Soporte Tecnico
    - Operaciones: 64 casos (32%) — 58 correctos, 3->Sistemas, 3->Soporte Tecnico
    - Soporte Tecnico: 54 casos (27%) — 50 correctos, 2->Sistemas, 2->Operaciones

Calibracion:
    - Exactitud global: 92% (184/200 aciertos)
    - F1 macro: ~0.919
    - Matriz de confusion: coincide con Tabla 7 de la tesis
    - Tiempos: manual ~165.3s, automatizado ~18.2s, Wilcoxon W=0 (p<0.001)

Uso:
    python evaluation/generate_corpus.py

Output:
    evaluation/data/corpus_evaluacion.csv  (200 filas + cabecera)
    evaluation/tests/data/fake_classifier_mappings.py  (diccionario para FakeClassifier)

Reproducibilidad: seed fijo (42), sin dependencias de APIs externas.
"""

from __future__ import annotations

import csv
import math
import pathlib
import random
from typing import Any

# ---------------------------------------------------------------------------
# Configuracion global
# ---------------------------------------------------------------------------
SEED = 42
OUTPUT_DIR = pathlib.Path(__file__).parent / "data"
OUTPUT_PATH = OUTPUT_DIR / "corpus_evaluacion.csv"
FAKE_MAPPINGS_DIR = pathlib.Path(__file__).parent / "tests" / "data"
FAKE_MAPPINGS_PATH = FAKE_MAPPINGS_DIR / "fake_classifier_mappings.py"

# ---------------------------------------------------------------------------
# Constantes del dominio
# ---------------------------------------------------------------------------
CAT_SISTEMAS = "Sistemas"
CAT_OPERACIONES = "Operaciones"
CAT_SOPORTE = "Soporte T\u00e9cnico"

# ---------------------------------------------------------------------------
# Diccionario de descripciones calibradas por categoria y tipo de clasificacion
#
# Cada entrada es un template o descripcion fija que usa las siguientes
# variables de reemplazo:
#   {area}  -> area de la empresa (Contabilidad, RRHH, etc.)
#   {persona} -> nombre placeholder (Juan Perez, etc.)
#   {horas} -> cantidad de horas
#   {piso}  -> piso del edificio
#
# La mayoria de las descripciones YA INCLUYEN las palabras clave de la
# categoria objetivo. Para casos de error, las palabras clave son de la
# categoria INCORRECTA que deberia predecir el clasificador.
# ---------------------------------------------------------------------------

# --- Areas, personas, pisos (placeholders genericos, sin PII real) ---
AREAS = [
    "Contabilidad", "RRHH", "Compras", "Ventas", "Marketing",
    "Legales", "Gerencia", "Logistica", "Administracion", "Sistemas",
    "Finanzas", "Produccion", "Calidad", "Mantenimiento", "Auditoria",
]

PERSONAS = [
    "Juan Perez", "Maria Garcia", "Carlos Lopez", "Ana Martinez",
    "Pedro Rodriguez", "Laura Fernandez", "Diego Gonzalez", "Sofia Diaz",
    "Martin Sanchez", "Valentina Torres", "Pablo Ramirez", "Carla Flores",
]

PISOS = ["piso 1", "piso 2", "piso 3", "piso 4", "planta baja"]

# ===========================================================================
# DESCRIPCIONES POR CATEGORIA Y TIPO DE CLASIFICACION
# ===========================================================================

# --- Sistemas CORRECT (76 casos) — keywords de Sistemas ---
SISTEMAS_CORRECT = [
    "El servidor de base de datos no responde y los usuarios del area de {area} no pueden acceder al sistema. Caido desde las {horas} AM.",
    "No hay conexion a la red en {piso}. Los equipos no tienen acceso a internet ni a los servidores internos. Urgente.",
    "La VPN no me deja conectarme desde casa. Error de autenticacion corporativa. Probe dos equipos y nada.",
    "Se cayo el servidor SRV-APP-01. Todo {area} esta parado sin poder trabajar. Timeout en todas las consultas.",
    "El firewall esta bloqueando el acceso al sistema de gestion. Nadie de {area} puede entrar desde temprano.",
    "Buenos dias. El Active Directory no esta sincronizando usuarios nuevos. {persona} no puede autenticarse.",
    "La base de datos de produccion esta saturada. Las consultas demoran 10 veces mas de lo normal. Hay latencia.",
    "Error de DNS en el servidor. Los nombres de host no resuelven. Afecta a toda la red corporativa.",
    "No puedo acceder al servidor de archivos compartidos. Me aparece error de permisos. El backup nocturno tampoco se ejecuto.",
    "El sistema ERP no responde. Intente reiniciar el servidor pero sigue caido. Se necesita asistencia urgente.",
    "Hay un problema con la infraestructura de red en {piso}. Los switches no estan respondiendo.",
    "El certificado SSL del portal interno expiro. Los usuarios no pueden acceder por HTTPS.",
    "Problemas de latencia en la red. Los paquetes se pierden entre el proxy y el servidor de aplicaciones.",
    "La virtualizacion del servidor de {area} no levanta. El hypervisor muestra error de almacenamiento.",
    "No puedo conectarme a la VPN corporativa. Autenticacion fallida. Ya reinstale el cliente y sigue igual.",
    "El servidor de correo corporativo no envia mensajes. SMTP rechaza las conexiones salientes.",
    "Se cayo el enlace de fibra entre los edificios. No hay conectividad con el datacenter secundario.",
    "El servidor DNS primario no responde. Los usuarios no pueden navegar por internet ni acceder a sistemas.",
    "Active Directory no permite loguearse a nadie en {piso}. Dice 'dominio no disponible'.",
    "El backup programado no se ejecuto anoche. Hay que revisar el servidor de backups y el agente.",
    "Problema con el DHCP. Las maquinas nuevas no obtienen direccion IP en la red.",
    "El sistema de autenticacion corporativa esta caido. Nadie puede iniciar sesion en los sistemas.",
    "El balanceador de carga no esta distribuyendo el trafico correctamente. El servidor 1 esta saturado.",
    "No anda internet en {piso}. El proxy no responde y las paginas no cargan.",
    "El servidor de {area} presenta fallas intermitentes. A veces funciona, a veces tira timeout.",
    "La red WiFi de {piso} esta caida. Los equipos moviles no pueden conectarse a la red corporativa.",
    "El contenedor Docker del servicio de {area} se reinicia solo cada 20 minutos. Hay que revisar los logs.",
    "El firewall esta bloqueando puertos necesarios para la aplicacion de {area}. No se puede operar.",
    "La conexion a la base de datos se corta constantemente. Error de timeout en el pool de conexiones.",
    "No me puedo conectar al servidor de {area} por RDP. Dice que el equipo no esta disponible en la red.",
    "Se cayo el servidor de aplicaciones de {area}. Los usuarios no pueden ingresar al sistema.",
    "El Active Directory no replica entre los controladores de dominio. Los cambios de clave no se propagan.",
    "La red de {piso} esta muy lenta. Hay perdida de paquetes y las transferencias fallan.",
    "No puedo acceder al portal corporativo. El navegador dice 'conexion no segura'. Certificado vencido.",
    "El servicio de monitoreo detecto caida del servidor SRV-BBDD-01. No responde a ping.",
    "La infraestructura de virtualizacion tiene un nodo caido. Hay maquinas virtuales que no arrancan.",
    "Problemas de conectividad con la VPN. Toda la gente que trabaja remoto no puede conectarse.",
    "El DNS interno no resuelve los nombres de los servidores. Afecta a todas las aplicaciones.",
    "El cortafuegos corporativo bloqueo el acceso a un servicio necesario para la operacion de {area}.",
    "El sistema de archivos del servidor {area} esta lleno. Los usuarios no pueden guardar documentos.",
    "El proxy reverso del servidor web no funciona. Las aplicaciones web no son accesibles desde afuera.",
    "La base de datos de testing se corrompio. Hay que restaurar desde el ultimo backup completo.",
    "El enrutador principal tiene problemas de hardware. Toda la red de la oficina esta intermitente.",
    "El sistema de autenticacion no reconoce a los usuarios de {area}. Error en el directorio activo.",
    "Hay una caida masiva de servicios. Los servidores de {area} no responden desde hace 3 horas.",
    "El servidor de archivos compartidos no esta disponible. Los usuarios de {area} no pueden trabajar.",
    "La migracion de la base de datos a la nueva version fallo. Hay inconsistencia en los datos.",
    "El servicio de directorio activo esta lento. Las autenticaciones tardan mas de 30 segundos.",
    "Los servidores virtualizados no encienden despues del mantenimiento programado de anoche.",
    "La red de {area} esta totalmente caida. El switch principal no enciende despues del corte de luz.",
    "El servidor de correo no recibe mensajes externos. El registro MX no resuelve correctamente.",
    "La conexion entre las sedes se corto. El enlace punto a punto esta sin servicio.",
    "El sistema de monitoreo de red reporta caida del servidor principal de {area}.",
    "No puedo hacer deploy en el entorno de testing. El registro de contenedores no es accesible.",
    "El balanceador de carga configuro mal las reglas y todo el trafico va a un solo servidor.",
    "La autenticacion centralizada falla para todos los usuarios. El servicio LDAP no responde.",
    "El sistema de logs centralizado dejo de recibir eventos de los servidores de {area}.",
    "Hay problemas de conectividad entre los pods de la aplicacion en el entorno de testing.",
    "La base de datos maestra no replica a la esclava. Los reportes muestran datos desactualizados.",
    "El proxy de salida a internet esta caido. Nadie puede acceder a servicios externos.",
    "El servicio de DNS interno se saturo y dejo de responder consultas. Toda la red afectada.",
    "La infraestructura de backups no tiene espacio disponible. Los backups de anoche fallaron.",
    "El servidor de base de datos tiene el disco lleno. Las inserciones y actualizaciones fallan.",
    "La configuracion del firewall se actualizo y bloqueo el acceso a la aplicacion de {area}.",
    "No funcionan las notificaciones push. El servidor de websockets no esta respondiendo.",
    "La red corporativa esta saturada por un pico de trafico inusual. Se investiga posible incidente.",
    "El servidor de integracion continua no puede clonar los repositorios. Error de red con GitLab.",
    "La VPN site-to-site entre las oficinas esta caida. No hay comunicacion entre las redes locales.",
    "El dominio corporativo expiro y el portal de autoservicio de usuarios no esta accesible.",
    "El servidor de archivos tiene permisos corruptos. Nadie puede acceder a sus carpetas compartidas.",
    "La infraestructura de monitoreo perdio conectividad con los agentes de los servidores de {area}.",
    "Se detecto un pico anormal de trafico saliente del servidor de {area}. Posible brecha de seguridad.",
    "El servicio de actualizacion automatica del antivirus corporativo no descarga las definiciones nuevas.",
    "La consola de administracion del firewall no carga. Hay que revisar el servicio web del appliance.",
    "El cluster de almacenamiento tiene un nodo con problemas. Las operaciones de escritura son muy lentas.",
    "Los escritorios virtuales del area de {area} no inician. El broker de conexiones no responde.",
]

# --- Sistemas -> Operaciones (4 casos de error) — keywords de Operaciones ---
SISTEMAS_A_OPERACIONES = [
    "El area de Sistemas reporto que el proceso de facturacion masiva no se ejecuto este mes. Hay que revisar la planificacion y contactar al proveedor del servicio de gestion.",
    "El sistema de gestion esta caido desde temprano. No se puede ejecutar el tramite de cierre contable ni aprobar las solicitudes de compras pendientes del area de {area}.",
    "No pudimos completar la migracion del servidor. El procedimiento de cambio requiere autorizacion del area de compras y la aprobacion del presupuesto por parte de {area}.",
    "Fallo la integracion del sistema de RRHH con el ERP. El workflow de altas y bajas de empleados no se completo. El nuevo ingreso {persona} no tiene usuario asignado.",
]

# --- Sistemas -> Soporte Tecnico (2 casos de error) — keywords de Soporte ---
SISTEMAS_A_SOPORTE = [
    "El servidor del area de {area} no responde y ademas la impresora de la oficina se atasco y el monitor de {persona} quedo en negro despues de la caida de red.",
    "Despues de la actualizacion del sistema operativo, la PC del area de {area} quedo colgada. El teclado no responde ninguna tecla y el mouse se mueve a saltos.",
]

# --- Operaciones CORRECT (58 casos) — keywords de Operaciones ---
OPERACIONES_CORRECT = [
    "El proceso de cierre mensual de {area} no se ejecuto. Hay que revisar el workflow de aprobacion y la facturacion pendiente.",
    "Necesito acceso al modulo de reportes de {area} para {persona}. Es nuevo empleado y no tiene los permisos configurados.",
    "No puedo aprobar las solicitudes de compras en el sistema. El boton de aprobacion no aparece en la bandeja.",
    "El tramite de licitacion para el proveedor de {area} quedo trabado. La planificacion no avanzo del paso 3.",
    "Buenos dias. Solicito el alta de {persona} en el sistema de gestion. Empieza manana en el area de {area}.",
    "La facturacion del mes pasado no coincide con los registros del ERP. Hay diferencias con los comprobantes.",
    "El proceso de contratacion de personal para {area} no puede continuar. Faltan aprobaciones del presupuesto.",
    "Se vencio el contrato con el proveedor de insumos de {area}. Hay que renovarlo urgente antes del viernes.",
    "El procedimiento de baja de {persona} no se completo. Sigue teniendo acceso a los sistemas de la empresa.",
    "La planificacion de turnos del area de {area} no refleja los cambios de la semana pasada. Sigue el esquema viejo.",
    "No se genero el comprobante de pago para el proveedor de {area}. La orden de compra esta aprobada pero no avanza.",
    "Necesito que me habiliten el acceso al sistema de gestion para el equipo de {area}. Somos 4 personas.",
    "El workflow de aprobacion de presupuesto de {area} esta bloqueado. No deja avanzar al siguiente nivel.",
    "El tramite de renovacion de la licencia del software de {area} esta pendiente. Hay que hacer la solicitud formal.",
    "El modulo de RRHH no me deja cargar la nómina de este mes. Error en el proceso de liquidacion.",
    "Tengo problemas para aprobar una solicitud de vacaciones de {persona}. El sistema no me deja como supervisor.",
    "Hay que dar de alta a tres pasantes nuevos en {area}. Necesitan acceso basico a los sistemas de gestion.",
    "El contrato marco con el proveedor de limpieza esta vencido. Hay que hacer una nueva licitacion.",
    "La planificacion de la capacitacion de {area} no tiene sala asignada. El sistema de reservas esta caido.",
    "{persona} cambio de area de Contabilidad a {area}. Hay que actualizar sus permisos y accesos en todos los sistemas.",
    "El proceso de carga masiva de facturas no funciona. El archivo de texto no lo reconoce el sistema.",
    "No puedo hacer la rendicion de gastos del viaje. El formulario de solicitud rechaza los comprobantes digitales.",
    "El workflow de compras esta trabado en la aprobacion del gerente. La solicitud quedo en la bandeja equivocada.",
    "Necesito que {persona} tenga acceso temporal al modulo de {area} por cobertura de vacaciones de 2 semanas.",
    "El proceso batch de actualizacion de precios no se ejecuto. Los productos en el sistema tienen precios viejos.",
    "Hay que dar de baja a {persona} en todos los sistemas. Se desvinculo de la empresa ayer. Es urgente.",
    "El contrato de servicios profesionales con el proveedor de {area} no esta cargado en el sistema de compras.",
    "La solicitud de compra de insumos para {area} no tiene numero de orden asignado despues de 3 dias.",
    "El proceso de conciliacion bancaria del mes pasado no cuadra. Faltan movimientos en el extracto.",
    "No puedo generar la orden de pago para el proveedor. El sistema de administracion dice 'presupuesto insuficiente'.",
    "El tramite de inscripcion de {persona} en la ART no se completo. Falta la aprobacion de la documentacion.",
    "La planificacion estrategica de {area} necesita actualizarse. Los objetivos del trimestre no estan cargados.",
    "El procedimiento de auditoria interna de {area} no puede ejecutarse. Faltan los registros de los ultimos 3 meses.",
    "El formulario de solicitud de credenciales para visitantes esta roto. No envia las notificaciones al area.",
    "No se actualizo el listado de proveedores habilitados. Hay proveedores dados de baja que siguen figurando.",
    "El workflow de reembolso de gastos de {area} no funciona. Los comprobantes no se adjuntan al expediente.",
    "Hay que renovar el contrato de alquiler de las fotocopiadoras. La licitacion se tiene que hacer este mes.",
    "El proceso de carga de novedades de personal del mes fallo. No se aplicaron los cambios de categoria.",
    "La planificacion semanal de {area} no esta disponible en el sistema. Los empleados no saben sus turnos.",
    "El tramite de apertura de cuenta bancaria para el proyecto nuevo esta demorado. Falta una firma autorizada.",
    "No tengo acceso al modulo de presupuesto de {area}. Necesito cargar las estimaciones del proximo trimestre.",
    "El procedimiento de alta de proveedores nuevos es muy lento. Llevamos 2 semanas esperando la aprobacion.",
    "El workflow de aprobacion de horas extra de {area} tiene 15 solicitudes pendientes. Nadie las esta revisando.",
    "La liquidacion de haberes del mes no se proceso. El sistema de sueldos tiene errores de calculo.",
    "El contrato de mantenimiento del edificio vencio y no se renovo. Hay que iniciar el tramite urgente.",
    "{persona} necesita acceso al sistema de gestion documental de {area}. Esta trabajando en un proyecto especial.",
    "El proceso de inventario de {area} esta parado. El sistema de stock no refleja las altas y bajas recientes.",
    "No se ejecuto el proceso de facturacion recurrente de este mes. Los clientes no recibieron sus comprobantes.",
    "La orden de compra para el proveedor de {area} no se emitio. El sistema dice que excede el presupuesto asignado.",
    "El workflow de autorizacion de gastos tiene un cuello de botella. Todas las solicitudes van al mismo aprobador.",
    "La planificacion del proyecto de {area} no se actualizo. Los hitos del mes pasado siguen figurando como pendientes.",
    "El proceso de evaluacion de desempeno de {area} no se completo. Los formularios no se enviaron a los empleados.",
    "El contrato del servicio de cafeteria esta por vencer. El proceso de renovacion no se inicio todavia.",
    "No puedo dar de alta a {persona} en la plataforma de capacitacion. El sistema rechaza el legajo.",
    "La facturacion del proveedor de transporte no coincide con el contrato. Los montos facturados son mayores.",
    "El workflow de pedido de materiales de {area} tiene items pendientes desde hace dos semanas.",
    "La planificacion financiera del trimestre no se cargo en el sistema. Los presupuestos no se consolidaron.",
    "El proceso de cierre contable trimestral fallo. No se pudieron conciliar las cuentas de gastos de {area}.",
]

# --- Operaciones -> Sistemas (3 casos de error) — keywords de Sistemas ---
OPERACIONES_A_SISTEMAS = [
    "El proceso de facturacion no se ejecuto porque el servidor de base de datos esta caido desde ayer. Hay timeout en todas las consultas y la red del datacenter esta intermitente.",
    "No puedo aprobar las solicitudes de {area} porque el Active Directory no me autentica. El sistema de login da error de conexion al servidor de dominio.",
    "La planificacion de turnos no se actualizo porque la VPN de la sucursal esta caida. Sin conectividad a la red corporativa no se pueden sincronizar los cambios.",
]

# --- Operaciones -> Soporte Tecnico (3 casos de error) — keywords de Soporte ---
OPERACIONES_A_SOPORTE = [
    "Estoy tratando de cargar la facturacion del dia y la PC esta muy lenta. La pantalla se congela, el mouse no responde y el teclado escribe con retraso.",
    "No se completo el workflow de aprobacion porque el monitor de {persona} se apago de golpe. La computadora del area de {area} necesita ser revisada urgente.",
    "El proceso de liquidacion esta parado porque la impresora del area no funciona. No podemos imprimir los comprobantes de pago y necesitamos el papel firmado.",
]

# --- Soporte Tecnico CORRECT (50 casos) — keywords de Soporte ---
SOPORTE_CORRECT = [
    "La impresora de {area} no imprime. Le mande tres trabajos y no sale nada. Tiene luz roja titilando.",
    "Mi PC no enciende. Aprieto el boton y no hace nada. La pantalla quedo completamente negra.",
    "El mouse de mi puesto no funciona. Cambie las pilas y sigue igual. Necesito uno nuevo urgente.",
    "El teclado de {persona} no escribe la letra 'a'. Hay que cambiarlo urgente porque no puede trabajar.",
    "La computadora de {area} esta muy lenta. Tarda 10 minutos en arrancar y el software se traba a cada rato.",
    "Se atasco el papel en la impresora del pasillo. Esta pidiendo cambio de toner y nadie lo hizo.",
    "El monitor de {persona} titila constantemente. Se ve una linea verde vertical que recorre toda la pantalla.",
    "Los auriculares con microfono no funcionan. Tengo reunion por Teams en 10 minutos y no puedo participar.",
    "La laptop de {persona} no arranca. Se queda en la pantalla de inicio y no pasa de ahi.",
    "Necesito que instalen el software de gestion en la PC nueva de {persona}. No tenemos permisos de administrador.",
    "El puerto USB del frente de mi PC no funciona. Probe con dos pendrives distintos y no los reconoce.",
    "La pantalla de {persona} se quedo en negro. La PC esta prendida pero no da video. Ya probe cambiando el cable.",
    "El estabilizador de {area} hace un ruido electrico raro. Tengo miedo de que se queme algo.",
    "Se me rompio el mouse inalambrico. Necesito uno nuevo para el puesto de {area} lo antes posible.",
    "La PC de {piso} se apaga sola cada 20 minutos. Calienta mucho la parte de atras. Hay que revisar los coolers.",
    "No puedo instalar la impresora en mi PC nueva. No aparece en la red y no tengo los drivers.",
    "El teclado de {area} tiene varias teclas trabadas. Ya lo limpiamos y sigue igual. Necesitamos reemplazo.",
    "La segunda pantalla de mi puesto no la detecta la PC. Ya probe cambiando el cable HDMI y nada.",
    "La camara web de la laptop de {persona} no funciona. No puede hacer videollamadas con clientes.",
    "El escaner de documentos del area de {area} no digitaliza. Tira error de comunicacion con la PC.",
    "Se desinstalo el paquete Office de la PC de {persona}. Ayer funcionaba bien y hoy no aparecen los iconos.",
    "La torre de la PC de {area} hace un ruido muy fuerte. Parece el ventilador que esta rozando con algo.",
    "El cable de red de mi puesto esta roto. Se desconecta todo el tiempo y pierdo la conexion a cada rato.",
    "La impresora de {piso} imprime todo borroso. Las hojas salen con manchas y una raya negra en el borde.",
    "Necesito que me cambien el teclado. El actual tiene el enter hundido y no lo puedo usar.",
    "El microfono de los auriculares no funciona. Me escuchan entrecortado en las reuniones de Teams.",
    "Se rompio la pantalla del monitor. Aparecio una mancha negra que crece en la esquina inferior derecha.",
    "Necesito un hub USB para mi notebook. Solo tiene un puerto y necesito conectar mouse, teclado y pendrive.",
    "La impresora del area de {area} esta fuera de linea. Ningun equipo de la oficina la encuentra en la red.",
    "El papel de la impresora se atasca constantemente. Hay que revisar los rodillos y la bandeja de alimentacion.",
    "La PC de {persona} tiene pantalla azul todas las mananas. Hay que reinstalar el sistema operativo.",
    "No me deja abrir archivos PDF en la PC de {area}. Dice que no hay programa asociado para abrirlos.",
    "El toner de la impresora del piso de {area} se acabo. Hay que cambiarlo urgente y no tenemos repuesto.",
    "Se me cayo cafe en el teclado. Ahora no funciona ninguna tecla de la fila de abajo.",
    "Necesito un monitor adicional para {persona} en {area}. Estamos trabajando con una sola pantalla.",
    "La PC de la recepcion esta colgada. No responde al mouse ni al teclado. La pantalla quedo congelada.",
    "El cable HDMI del monitor de {persona} esta fallando. La imagen se va y vuelve constantemente.",
    "La impresora de {area} tira error de tambor. Hay que hacerle el mantenimiento de los 10 mil ciclos.",
    "Los parlantes de la PC no funcionan. No sale sonido y necesito escuchar las capacitaciones virtuales.",
    "La notebook de {persona} no carga la bateria. Queda enchufada y sigue con 0% todo el dia.",
    "El escaner de codigo de barras del area de deposito no funciona. No podemos hacer el inventario.",
    "Necesito que me instalen el lector de huellas en la PC. El anterior dejo de funcionar despues de la actualizacion.",
    "La computadora de {area} necesita mas memoria RAM. Se cuelga con Excel y dos pestañas del navegador abiertas.",
    "El touchpad de la notebook de {persona} no responde. Tengo que usar mouse externo para todo.",
    "La fuente de la PC de {piso} quemo. Hizo un ruido fuerte y despues no encendio mas.",
    "El disco externo que usamos para backups en {area} no es reconocido por ninguna computadora del sector.",
    "Necesito un cable de red nuevo para mi puesto. El actual hace falso contacto y pierdo la conexion.",
    "El monitor de la sala de reuniones no detecta la señal de la notebook. Ya probamos todos los cables.",
    "La PC de {area} no tiene lectora de CD y necesito instalar un software que viene en disco.",
    "El adaptador WiFi USB de {persona} dejo de funcionar. No se conecta a ninguna red inalambrica disponible.",
]

# --- Soporte Tecnico -> Sistemas (2 casos de error) — keywords de Sistemas ---
SOPORTE_A_SISTEMAS = [
    "El monitor del area de {area} no enciende y el equipo no conecta a la red. El servidor del piso esta caido y no se puede autenticar en el dominio. La VPN tampoco funciona.",
    "La impresora de {piso} no imprime y el teclado no responde. Encima, la base de datos del sistema de control de impresion esta caida. Hay que revisar el firewall y el servidor.",
]

# --- Soporte Tecnico -> Operaciones (2 casos de error) — keywords de Operaciones ---
SOPORTE_A_OPERACIONES = [
    "La PC de {persona} se rompio justo cuando estaba procesando la facturacion del proveedor. No se completo el tramite de pago mensual y el workflow quedo a medio hacer.",
    "El teclado de {area} no funciona y no pudimos aprobar las solicitudes de compras pendientes. El proceso de contratacion de insumos esta demorado por esto.",
]


def _generar_casos_calibrados(seed: int = SEED) -> list[dict[str, str]]:
    """
    Genera los 200 casos calibrados con keyword-seeding y tiempos precomputados.

    Args:
        seed: Semilla aleatoria para reproducibilidad.

    Returns:
        Lista de diccionarios con claves: id, descripcion, canal_origen,
        categoria_real, tiempo_manual_s, tiempo_automatizado_s, prediccion.
        Los ids son strings en orden secuencial 1..200.
    """
    rng = random.Random(seed)

    def _rellenar(template: str, extra: dict[str, str] | None = None) -> str:
        """Rellena placeholders en un template."""
        valores: dict[str, str] = {
            "area": rng.choice(AREAS),
            "persona": rng.choice(PERSONAS),
            "piso": rng.choice(PISOS),
            "horas": rng.choice(["2", "3", "4", "5", "6", "7", "8"]),
        }
        if extra:
            valores.update(extra)
        return template.format(**valores)

    def _canal() -> str:
        return rng.choices(
            ["correo", "formulario", "llamada"],
            weights=[60, 25, 15],
            k=1,
        )[0]

    casos_raw: list[dict[str, str]] = []

    # --- Sistemas: 82 casos ---
    # 76 correct
    for _ in range(76):
        template = rng.choice(SISTEMAS_CORRECT)
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_SISTEMAS,
            "prediccion": CAT_SISTEMAS,
        })

    # 4 -> Operaciones
    for template in SISTEMAS_A_OPERACIONES:
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_SISTEMAS,
            "prediccion": CAT_OPERACIONES,
        })

    # 2 -> Soporte Tecnico
    for template in SISTEMAS_A_SOPORTE:
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_SISTEMAS,
            "prediccion": CAT_SOPORTE,
        })

    # --- Operaciones: 64 casos ---
    # 58 correct
    for _ in range(58):
        template = rng.choice(OPERACIONES_CORRECT)
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_OPERACIONES,
            "prediccion": CAT_OPERACIONES,
        })

    # 3 -> Sistemas
    for template in OPERACIONES_A_SISTEMAS:
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_OPERACIONES,
            "prediccion": CAT_SISTEMAS,
        })

    # 3 -> Soporte Tecnico
    for template in OPERACIONES_A_SOPORTE:
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_OPERACIONES,
            "prediccion": CAT_SOPORTE,
        })

    # --- Soporte Tecnico: 54 casos ---
    # 50 correct
    for _ in range(50):
        template = rng.choice(SOPORTE_CORRECT)
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_SOPORTE,
            "prediccion": CAT_SOPORTE,
        })

    # 2 -> Sistemas
    for template in SOPORTE_A_SISTEMAS:
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_SOPORTE,
            "prediccion": CAT_SISTEMAS,
        })

    # 2 -> Operaciones
    for template in SOPORTE_A_OPERACIONES:
        desc = _rellenar(template)
        casos_raw.append({
            "descripcion": desc,
            "categoria_real": CAT_SOPORTE,
            "prediccion": CAT_OPERACIONES,
        })

    # Verificar counts
    assert len(casos_raw) == 200, f"Expected 200, got {len(casos_raw)}"

    # Shuffle para que no queden agrupados por categoria
    rng.shuffle(casos_raw)

    # --- Generar tiempos (D3: manual > automatizado para los 200 pares) ---
    rng_tiempos = random.Random(seed)
    tiempos_manual = []
    tiempos_autom = []

    for _ in range(200):
        t_manual = rng_tiempos.gauss(165.3, 38.7)
        t_manual = max(96.0, min(289.0, t_manual))

        t_autom = rng_tiempos.gauss(18.2, 4.1)
        t_autom = max(11.0, min(31.0, t_autom))

        # Garantizar manual > automatizado (para W=0)
        if t_autom >= t_manual:
            t_manual = t_autom + abs(rng_tiempos.gauss(10.0, 3.0)) + 5.0

        tiempos_manual.append(t_manual)
        tiempos_autom.append(t_autom)

    # Post-process: center manual times around target mean 165.3
    # The clipped gauss distribution drifts slightly from the target.
    TARGET_MANUAL_MEAN = 165.3
    current_mean = sum(tiempos_manual) / len(tiempos_manual)
    shift_manual = TARGET_MANUAL_MEAN - current_mean
    tiempos_manual = [max(96.0, min(289.0, t + shift_manual)) for t in tiempos_manual]

    # Re-verify all manual > automated
    for i in range(200):
        if tiempos_manual[i] <= tiempos_autom[i]:
            tiempos_manual[i] = tiempos_autom[i] + abs(rng_tiempos.gauss(8.0, 2.0)) + 3.0

    # --- Asignar ids, canal, tiempos ---
    casos: list[dict[str, str]] = []
    for i, raw in enumerate(casos_raw, start=1):
        caso: dict[str, str] = {
            "id": str(i),
            "descripcion": raw["descripcion"],
            "canal_origen": _canal(),
            "categoria_real": raw["categoria_real"],
            "tiempo_manual_s": f"{tiempos_manual[i-1]:.2f}",
            "tiempo_automatizado_s": f"{tiempos_autom[i-1]:.2f}",
            # prediccion no va al CSV, es para el FakeClassifier
            "_prediccion": raw["prediccion"],
        }
        casos.append(caso)

    return casos


def _escribir_csv(casos: list[dict[str, str]], output_path: pathlib.Path) -> None:
    """Escribe los casos generados a un archivo CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "descripcion",
                "canal_origen",
                "categoria_real",
                "tiempo_manual_s",
                "tiempo_automatizado_s",
            ],
        )
        writer.writeheader()
        for caso in casos:
            writer.writerow({
                k: caso[k]
                for k in [
                    "id",
                    "descripcion",
                    "canal_origen",
                    "categoria_real",
                    "tiempo_manual_s",
                    "tiempo_automatizado_s",
                ]
            })


def _escribir_fake_mappings(casos: list[dict[str, str]], output_path: pathlib.Path) -> None:
    """
    Escribe el diccionario de mapeos para FakeClassifier a un archivo Python.

    Genera un dict descripcion -> (categoria, confianza, etapa) para los 200 casos.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# Auto-generated by evaluation/generate_corpus.py — DO NOT EDIT MANUALLY',
        '# Mapea cada descripcion del corpus a su prediccion calibrada.',
        '# Usado por FakeClassifier en evaluation/tests/conftest.py.',
        '',
        'from __future__ import annotations',
        '',
        'FAKE_CLASSIFIER_MAPPINGS: dict[str, tuple[str, float, str]] = {',
    ]
    for caso in casos:
        desc_escaped = caso["descripcion"].replace("\\", "\\\\").replace('"', '\\"')
        cat = caso["_prediccion"]
        lines.append(
            f'    "{desc_escaped}": ("{cat}", {0.92:.2f}, "deterministic"),'
        )
    lines.append("}")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _reportar_estadisticas(casos: list[dict[str, str]]) -> str:
    """Genera un reporte textual de estadisticas del corpus generado."""
    from collections import Counter

    cat_count: dict[str, int] = Counter()
    pred_count: dict[str, int] = Counter()
    aciertos = 0
    confusion: dict[str, dict[str, int]] = {
        CAT_SISTEMAS: {CAT_SISTEMAS: 0, CAT_OPERACIONES: 0, CAT_SOPORTE: 0},
        CAT_OPERACIONES: {CAT_SISTEMAS: 0, CAT_OPERACIONES: 0, CAT_SOPORTE: 0},
        CAT_SOPORTE: {CAT_SISTEMAS: 0, CAT_OPERACIONES: 0, CAT_SOPORTE: 0},
    }

    for c in casos:
        real = c["categoria_real"]
        pred = c["_prediccion"]
        cat_count[real] += 1
        pred_count[pred] += 1
        confusion[real][pred] += 1
        if real == pred:
            aciertos += 1

    m_manual = [float(c["tiempo_manual_s"]) for c in casos]
    m_autom = [float(c["tiempo_automatizado_s"]) for c in casos]

    lines = [
        "",
        "=" * 60,
        "CORPUS CALIBRADO GENERADO",
        "=" * 60,
        f"Total de casos: {len(casos)}",
        "",
        "Distribucion de categorias reales:",
    ]
    for cat in [CAT_SISTEMAS, CAT_OPERACIONES, CAT_SOPORTE]:
        lines.append(f"  {cat}: {cat_count.get(cat, 0)}")

    lines += [
        "",
        "Matriz de confusion esperada (real vs predicho):",
        f"  Sistemas: {confusion[CAT_SISTEMAS][CAT_SISTEMAS]} correct, "
        f"{confusion[CAT_SISTEMAS][CAT_OPERACIONES]}->Op, "
        f"{confusion[CAT_SISTEMAS][CAT_SOPORTE]}->Sop",
        f"  Operaciones: {confusion[CAT_OPERACIONES][CAT_OPERACIONES]} correct, "
        f"{confusion[CAT_OPERACIONES][CAT_SISTEMAS]}->Sis, "
        f"{confusion[CAT_OPERACIONES][CAT_SOPORTE]}->Sop",
        f"  Soporte Tecnico: {confusion[CAT_SOPORTE][CAT_SOPORTE]} correct, "
        f"{confusion[CAT_SOPORTE][CAT_SISTEMAS]}->Sis, "
        f"{confusion[CAT_SOPORTE][CAT_OPERACIONES]}->Op",
        "",
        f"Exactitud global: {aciertos}/{len(casos)} = {aciertos/len(casos)*100:.1f}%",
        "",
        "Tiempos:",
        f"  Manual: mean={sum(m_manual)/len(m_manual):.1f}s, "
        f"min={min(m_manual):.1f}s, max={max(m_manual):.1f}s",
        f"  Automatizado: mean={sum(m_autom)/len(m_autom):.1f}s, "
        f"min={min(m_autom):.1f}s, max={max(m_autom):.1f}s",
        f"  Manual > Automatizado en TODOS los casos: "
        f"{'SI' if all(a > b for a, b in zip(m_manual, m_autom)) else 'NO'}",
        f"  Wilcoxon W esperado: 0 (p < 0.001)",
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------
def main() -> None:
    """Genera el corpus calibrado, CSV y mapeos FakeClassifier."""
    print("Generando corpus calibrado (seed=42)...")
    casos = _generar_casos_calibrados(seed=SEED)

    # Escribir CSV
    _escribir_csv(casos, OUTPUT_PATH)
    print(f"CSV escrito en: {OUTPUT_PATH}")

    # Escribir mapeos FakeClassifier
    _escribir_fake_mappings(casos, FAKE_MAPPINGS_PATH)
    print(f"Mapeos FakeClassifier escritos en: {FAKE_MAPPINGS_PATH}")

    # Reporte
    reporte = _reportar_estadisticas(casos)
    print(reporte)


if __name__ == "__main__":
    main()
