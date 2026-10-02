# Marco legal argentino de protección de datos personales (estado a 2026)

Documento de investigación para la tesis "Automatización de Mesa de Ayuda" (UTN).
Alcance: régimen argentino aplicable a un sistema que recolecta datos personales de
empleados y llamantes, pseudonimiza campos sensibles, y transfiere fragmentos de texto a
proveedores de inferencia (Google Gemini) y telefonía (Twilio) con sede en Estados Unidos.

Fecha de acceso a las fuentes: 1 de octubre de 2026.
Método: verificación contra fuentes oficiales (InfoLEG/Boletín Oficial, AAIP,
Comisión Europea) y, de forma complementaria, análisis de estudios jurídicos. Los
proyectos de ley se contrastaron sobre el texto PDF descargado del Congreso.

Advertencia: este documento es un relevamiento informativo, no asesoramiento jurídico.
Las conclusiones de "Nivel de certeza" se refieren a la verificación de la fuente, no a la
interpretación jurídica definitiva.

---

## Resumen ejecutivo

1. La Ley 25.326 (2000) sigue siendo la ley vigente en 2026. No fue reemplazada ni
   sustituida por una ley integral nueva.
2. El proyecto de reforma alineado con el RGPD (Mensaje 87/2023) caducó parlamentariamente.
   Durante 2025 y 2026 se presentaron varios proyectos nuevos que continúan en trámite; a la
   fecha de acceso no se verificó la sanción de ninguna ley de reforma integral.
3. La autoridad de aplicación es la Agencia de Acceso a la Información Pública (AAIP),
   ente autárquico en la órbita de la Jefatura de Gabinete de Ministros, con la Dirección
   Nacional de Protección de Datos Personales (DNPDP) como área técnica.
4. No existe en la Ley 25.326 una obligación general y autónoma de notificación de brechas
   de seguridad a la autoridad. El deber aparece únicamente en los proyectos de reforma (72
   horas) y en regímenes sectoriales. La Resolución AAIP 47/2018 aprueba medidas de
   seguridad "recomendadas", sin una obligación de notificación con plazo.
5. Para transferencias a Estados Unidos rige el artículo 12 de la Ley 25.326: Estados Unidos
   NO integra la lista argentina de países con nivel adecuado, por lo que se requiere
   consentimiento expreso, cláusulas contractuales modelo (Disposición DNPDP 60/2016 y
   Resolución AAIP 198/2023) o normas corporativas vinculantes (Resolución AAIP 159/2018).
6. La decisión de adecuación de la Unión Europea respecto de Argentina (Decisión
   2003/490/CE) sigue vigente y fue revalidada en enero de 2024; la Comisión Europea
   mantiene a Argentina en su lista de países adecuados a la fecha de acceso.
7. Novedades 2025-2026 relevantes: guía de IA de la AAIP, programada creada por Resolución
   AAIP 161/2023 y Resolución AAIP 145/2025; criterios sobre decisiones automatizadas
   (Resolución AAIP 4/2019); normas sectoriales de IA del BCRA (2026) y del sector público
   (SIGEN 2026, MPF 2026); y varios proyectos legislativos sobre IA/transparencia
   algorítmica. Argentina sigue sin una ley nacional integral de IA.

---

## 1. Vigencia de la Ley 25.326 y estado de la reforma

### 1.1 Norma vigente

La Ley 25.326 de Protección de los Datos Personales fue sancionada el 4 de octubre de 2000
y promulgada parcialmente el 30 de octubre de 2000. Su decreto reglamentario es el Decreto
1558/2001, del 29 de noviembre de 2001. A la fecha de acceso, la AAIP la presenta como la
normativa vigente y en proceso de actualización, no como norma derogada.

Fuentes:
- InfoLEG, Ley 25.326 (texto completo): http://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/norma.htm (acceso 2026-10-01).
- AAIP, "Protección de datos personales": https://www.argentina.gob.ar/aaip/datospersonales (acceso 2026-10-01).
- AAIP, "Obligaciones de los responsables": https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones (acceso 2026-10-01).

Nivel de certeza: ALTO.

### 1.2 El proyecto de reforma alineado con el RGPD (2023)

La AAIP impulsó un proceso participativo (2022) que derivó en un anteproyecto y, luego, en
el Mensaje 87/2023 del Poder Ejecutivo Nacional (firmado por Alberto Fernández y Agustín
Rossi), remitido a la Honorable Cámara de Diputados. Ese proyecto NO fue sancionado:
conforme al análisis del estudio Bruchou & Funes de Rioja (junio de 2025), el proyecto del
Poder Ejecutivo "caducó parlamentariamente". El antecedente de 2018 también había perdido
estado parlamentario, según la propia AAIP.

Fuentes:
- AAIP, "Proyecto de Ley de Protección de Datos Personales": https://www.argentina.gob.ar/aaip/datospersonales/proyecto-ley-datos-personales (acceso 2026-10-01).
- Bruchou & Funes de Rioja, "Protección de Datos Personales: se presentó un nuevo Proyecto de Ley en la Cámara de Diputados", 9 de junio de 2025: https://bruchoufunes.com/proteccion-de-datos-personales-se-presento-un-nuevo-proyecto-de-ley-en-la-camarade-diputados/ (acceso 2026-10-01).
- Texto del Mensaje 87/2023: https://www.argentina.gob.ar/sites/default/files/mensajeyproyecto_leypdp2023.pdf (descargado y verificado 2026-10-01).

Nivel de certeza: ALTO (caducidad).

### 1.3 Proyectos presentados en 2025-2026 (no sancionados)

Se verificó la existencia de múltiples proyectos que modifican total o parcialmente la Ley
25.326. Ninguno fue sancionado a la fecha de acceso:

- Proyecto del diputado Pablo Carro (Unión por la Patria), presentado el 29 de abril de
  2025; expediente 1948-D-2025. Mantiene el enfoque del proyecto de 2023 e incorpora
  "dato inferido", reciprocidad en transferencias internacionales, y una unidad de multa
  inicial de AR$ 100.000 actualizable semestralmente.
- Propuesta publicada el 25 de junio de 2025 en el Portal de Leyes Abiertas, impulsada por
  el diputado Martín Yeza (fuente secundaria; no se accedió al texto íntegro).
- Expediente 3540-D-2025: "Transparencia Algorítmica"; modifica la Ley 25.326 para
  incorporar transparencia algorítmica, derecho a la explicación, responsabilidad
  informativa y auditoría de sistemas automatizados.
- Expediente 2968-D-2025: modificación de la Ley 25.326 para incorporar protecciones
  especiales a niñas, niños y adolescentes (consentimiento desde los 16 años, restricciones
  sobre datos sensibles y juegos en línea).
- Antecedente citado por fuentes secundarias: expediente S-0644/2025 del Senado (versión
  preliminar; no verificado el texto).

Fuentes:
- Bruchou & Funes de Rioja, 9 de junio de 2025 (proyecto Carro; enlace al PDF 1948-D-2025): https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2025/PDF2025/TP2025/1948-D-2025.pdf (descargado 2026-10-01).
- PDF 3540-D-2025: https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2025/PDF2025/TP2025/3540-D-2025.pdf (descargado 2026-10-01).
- PDF 2968-D-2025: https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2025/PDF2025/TP2025/2968-D-2025.pdf (descargado 2026-10-01).
- Abogados.com.ar, "Protección de Datos Personales: Propuesta de Ley" (25 de junio de 2025): https://abogados.com.ar/proteccion-de-datos-personales-propuesta-de-ley/37067 (acceso 2026-10-01).
- vLex Argentina, "PROYECTO DE LEY DE PROTECCION DE DATOS PERSONALES", expediente S-0644/2025: https://ar.vlex.com/vid/proyecto-ley-proteccion-datos-1079649899 (acceso 2026-10-01).

Nivel de certeza: ALTO para la existencia y el contenido de los PDF verificados; MEDIO para
los proyectos conocidos solo por fuente secundaria (Yeza, S-0644/2025).

### 1.4 Ley nacional de IA

No existe una ley nacional integral de inteligencia artificial. Una nota de seguimiento
regulatorio de septiembre de 2026 lo afirma de forma explícita y documenta el estado de los
expedientes. El expediente S. 1747/23 (Senado, sobre desarrollo y utilización de sistemas de
IA) caducó el 28 de febrero de 2025 y fue archivado el 11 de julio de 2025; se registra una
nueva presentación como S. 71/25. La Cámara de Diputados registra el expediente 2912-D-2026
(18 de junio de 2026), sobre régimen de IA y protección de datos en el sector público.

Fuente:
- Mundo IA, "Argentina aún no tiene una ley integral de IA: qué obligaciones existen", 25 de septiembre de 2026: https://www.mundoia.com.ar/regulacion-inteligencia-artificial-argentina-reglas-vigentes/ (acceso 2026-10-01).

Nivel de certeza: MEDIO (fuente periodística especializada que cita fichas parlamentarias;
no se verificó cada ficha directamente).

---

## 2. Autoridad de aplicación

La autoridad de aplicación y órgano de control de la Ley 25.326 es la Agencia de Acceso a la
Información Pública (AAIP), ente autárquico con autonomía funcional en la órbita de la
Jefatura de Gabinete de Ministros. La transferencia de competencias desde la ex Dirección
Nacional de Protección de Datos Personales (DNPDP, antes en el Ministerio de Justicia) hacia
la AAIP se instrumentó por el Decreto 746/2017 y el Decreto 899/2017. La Resolución AAIP
4/2019 y la Resolución AAIP 47/2018 citan expresamente esta cadena normativa. La DNPDP
subsiste como área técnica dentro de la AAIP; su titular actual es la Mg. Violeta Paulero.

Disposiciones y actos relevantes para el sector privado:
- Resolución AAIP 4/2019 (BO 16-01-2019): criterios orientadores e indicadores de mejores
  prácticas, "de observancia obligatoria" para los sujetos alcanzados por la Ley 25.326.
  Incluye criterios sobre video vigilancia, datos biométricos, consentimiento, cesión entre
  organismos públicos, menores y decisiones automatizadas.
- Resolución AAIP 47/2018 (BO 25-07-2018): medidas de seguridad recomendadas para el
  tratamiento y conservación de datos personales en medios informatizados y no
  informatizados (deroga las Disposiciones DNPDP 11/2006 y 9/2008).
- Resolución AAIP 14/2018: información al titular exhibida en sitio visible.
- Disposición DNPDP 60/2016 y Resolución AAIP 34/2019: países con nivel adecuado y
  cláusulas contractuales modelo.
- Resolución AAIP 159/2018: normas corporativas vinculantes.
- Resolución AAIP 198/2023: adopción de las Cláusulas Contractuales Modelo de la RIPD.
- Resolución AAIP 161/2023: Programa Nacional de Transparencia y Protección de Datos
  Personales en el uso de la Inteligencia Artificial.

Fuentes:
- AAIP, "Obligaciones de los responsables": https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones (acceso 2026-10-01).
- Resolución AAIP 4/2019 (texto original InfoLEG): https://www.argentina.gob.ar/normativa/nacional/resolucion-4-2019-318874/texto (acceso 2026-10-01).
- Resolución AAIP 47/2018 (Boletín Oficial): https://www.boletinoficial.gob.ar/detalleAviso/primera/188654/20180725 (acceso 2026-10-01).
- AAIP, "Transferencias internacionales": https://www.argentina.gob.ar/transferencias-internacionales (acceso 2026-10-01).
- Portal Nacional de Transparencia (Programa de IA, Resolución 161/2023): https://portal.transparencia.gob.ar/transparencia/transparenciaAlgoritmica (acceso 2026-10-01).

Nivel de certeza: ALTO. La continuidad de la AAIP bajo Jefatura de Gabinete en 2026 se
infiere de los sitios oficiales vigentes a la fecha de acceso.

No verificado: existencia de una reorganización administrativa posterior que hubiera
renombrado o reubicado la AAIP después de la fecha de los actos citados.

---

## 3. Obligaciones del responsable

### 3.1 Inscripción de bases de datos

El artículo 21 de la Ley 25.326 obliga a inscribir en el Registro Nacional de Bases de Datos
Personales los archivos, registros, bases o bancos de datos públicos y privados destinados a
proporcionar informes. El artículo 24 extiende la inscripción a los particulares que formen
archivos no destinados a uso exclusivamente personal. El incumplimiento habilita las
sanciones del Capítulo VI. La AAIP ofrece el trámite de inscripción.

Fuente:
- Ley 25.326, arts. 21 y 24: http://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/norma.htm (acceso 2026-10-01).
- AAIP, "Obligaciones de los responsables" e inscripción: https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones (acceso 2026-10-01).

Nivel de certeza: ALTO. Matiz interpretativo: el alcance de la obligación respecto de bases
de uso interno (no destinadas a dar informes) es discutido; el artículo 24 sugiere que la
inscripción es exigible para todo archivo que no sea de uso exclusivamente personal.

### 3.2 Base de licitud y consentimiento

El artículo 5 exige consentimiento libre, expreso e informado, que debe constar por escrito
o por otro medio equiparable. El artículo 5, inciso 2, enumera excepciones (fuentes de
acceso público irrestricto, funciones del Estado u obligación legal, listados tasados,
relación contractual/científica/profesional cuando resulte necesario para su cumplimiento,
y entidades financieras). El proyecto de reforma de 2025 incorpora la exigencia de
comunicación previa al titular cuando se invoque el interés legítimo.

Fuentes:
- Ley 25.326, art. 5 (texto en InfoLEG, ver 1.1).
- Bruchou & Funes de Rioja, 9 de junio de 2025 (novedad sobre interés legítimo).

Nivel de certeza: ALTO.

### 3.3 Deber de información

El artículo 6 obliga a informar previamente, de forma expresa y clara: finalidad y
destinatarios; existencia e identidad del responsable; carácter obligatorio o facultativo de
las respuestas; consecuencias de proporcionar o no los datos; y la posibilidad de ejercer
los derechos de acceso, rectificación y supresión. La Resolución AAIP 14/2018 regula la
exhibición de esta información en sitio visible.

Fuentes:
- Ley 25.326, art. 6; Resolución AAIP 14/2018 (referida en https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones).

Nivel de certeza: ALTO.

### 3.4 Derechos ARCO y plazos

- Acceso (art. 14): el responsable debe responder dentro de los DIEZ (10) DÍAS CORRIDOS de
  la intimación fehaciente. Ejercicio gratuito a intervalos no inferiores a seis meses,
  salvo interés legítimo acreditado.
- Rectificación, actualización o supresión (art. 16): plazo máximo de CINCO (5) DÍAS
  HÁBILES desde el reclamo o desde que se advierte el error. En caso de cesión o
  transferencia, el responsable debe notificar la rectificación o supresión al cesionario
  dentro del quinto día hábil.
- Oposición: la Ley 25.326 no enumera un derecho autónomo de "oposición" separado; prevé el
  derecho de acceso y el de rectificación/actualización/supresión, más el retiro o bloqueo
  del nombre en bases con fines publicitarios (art. 27) y la impugnación de valoraciones
  personales (art. 20). El acrónimo "ARCO" proviene de la práctica comparada y de los
  proyectos de reforma; conviene no atribuirle a la ley vigente un derecho de oposición
  genérico.

Observación para la tesis: la sección legal actual de la tesis (v7) afirma un plazo de
"cinco días corridos" para rectificación o supresión. La ley dice CINCO DÍAS HÁBILES
(art. 16, inc. 2). Corresponde corregir ese punto.

Fuentes:
- Ley 25.326, arts. 14, 16, 20 y 27 (texto InfoLEG).

Nivel de certeza: ALTO. La afirmación sobre la inexistencia de un derecho autónomo de
oposición es una lectura del texto legal; nivel de certeza ALTO sobre el texto, MEDIO sobre
la calificación dogmática.

### 3.5 Seguridad y confidencialidad

El artículo 9 obliga a adoptar medidas técnicas y organizativas necesarias para garantizar
seguridad y confidencialidad, evitar adulteración, pérdida, consulta o tratamiento no
autorizado, y detectar desviaciones. El artículo 10 impone el deber de confidencialidad, que
subsiste tras finalizar la relación. La Resolución AAIP 47/2018 aprueba las medidas de
seguridad "recomendadas" para medios informatizados y no informatizados.

Fuentes:
- Ley 25.326, arts. 9 y 10; Resolución AAIP 47/2018 (BO 25-07-2018).

Nivel de certeza: ALTO.

### 3.6 Datos sensibles

El artículo 7 prohíbe la formación de archivos que revelen directa o indirectamente datos
sensibles y limita su tratamiento a razones de interés general autorizadas por ley o a
finalidades estadísticas/científicas con datos no identificables. El artículo 2 define datos
sensibles (origen racial o étnico, opiniones políticas, convicciones religiosas o morales,
afiliación sindical, salud, vida sexual).

Fuente: Ley 25.326, arts. 2 y 7.

Nivel de certeza: ALTO.

---

## 4. Notificación de brechas de seguridad

### 4.1 Régimen vigente (Ley 25.326)

La Ley 25.326 NO contiene una obligación general y autónoma de notificar brechas de
seguridad a la autoridad de aplicación ni a los titulares. El texto legal relevante (arts. 9
y 10) exige seguridad y confidencialidad, pero no establece un deber de notificación con
plazo. La Resolución AAIP 47/2018 aprueba medidas de seguridad calificadas como
"recomendadas"; no introduce una obligación de notificación con plazo determinado.

Fuentes:
- Ley 25.326, arts. 9 y 10 (texto InfoLEG); verificación de ausencia de artículo de
  notificación en el texto completo (acceso 2026-10-01).
- Resolución AAIP 47/2018 (acceso 2026-10-01).

Nivel de certeza: ALTO sobre la ausencia de una obligación general en el texto de la ley.
No verificado: que exista una resolución administrativa específica de la AAIP (distinta de
las citadas) que imponga notificación de incidentes al sector privado.

### 4.2 Régimenes sectoriales

Existen obligaciones de reporte de incidentes en sectores regulados (por ejemplo, entidades
financieras alcanzadas por normas del Banco Central, y servicios de telecomunicaciones). No
se verificaron en esta investigación los números exactos de las comunicaciones o
resoluciones sectoriales aplicables, por lo que se listan como pendientes en la sección
"No verificado".

Nivel de certeza: MEDIO (existencia de regímenes sectoriales); BAJO para el detalle normativo.

### 4.3 Proyectos de reforma

Los proyectos de reforma relevados sí incorporan una obligación de notificación:
- Artículo 21 del proyecto del Poder Ejecutivo 2023 (Mensaje 87/2023): el responsable debe
  notificar a la autoridad dentro de las SETENTA Y DOS (72) HORAS de tomar conocimiento del
  incidente, con posibilidad de solicitar extensión del plazo; y debe informar al titular
  en lenguaje claro, o mediante comunicación pública si el esfuerzo es desproporcionado.
- El proyecto Carro 1948-D-2025 reproduce el mismo artículo 21 con idéntico plazo de 72
  horas.

Estos proyectos NO son ley a la fecha de acceso.

Fuentes:
- PDF Mensaje 87/2023, artículo 21 (descargado 2026-10-01).
- PDF 1948-D-2025, artículo 21 (descargado 2026-10-01).

Nivel de certeza: ALTO (contenido de los proyectos); ALTO (no están sancionados).

---

## 5. Transferencias internacionales

### 5.1 Regla general y lista de países adecuados

El artículo 12 de la Ley 25.326 prohíbe la transferencia de datos personales a países u
organismos internacionales o supranacionales que no proporcionen niveles de protección
adecuados, con excepciones tasadas (colaboración judicial internacional; intercambio de
datos médicos para tratamiento o investigación epidemiológica; transferencias bancarias o
bursátiles; tratados internacionales de los que Argentina sea parte; cooperación entre
organismos de inteligencia). El Decreto 1558/2001 reglamenta el artículo y la AAIP es la
autoridad competente para evaluar la adecuación de otros países.

La Disposición DNPDP 60/2016 y la Resolución AAIP 34/2019 establecen los países
considerados adecuados: Estados miembros de la Unión Europea y del EEE; Reino Unido;
Suiza; Guernsey; Jersey; Isla de Man; Islas Feroe; Canadá (solo sector privado); Andorra;
Nueva Zelanda; Uruguay; e Israel (solo tratamiento automatizado).

Estados Unidos NO integra la lista de países adecuados.

Fuentes:
- Ley 25.326, art. 12 (texto InfoLEG).
- AAIP, "Transferencias internacionales": https://www.argentina.gob.ar/transferencias-internacionales (acceso 2026-10-01).
- Disposición DNPDP 60/2016: https://www.argentina.gob.ar/sites/default/files/disp_e2016_60.pdf (acceso 2026-10-01).

Nivel de certeza: ALTO.

### 5.2 Mecanismos para transferir a países no adecuados (los EE. UU.)

Para transferir a Estados Unidos se requiere alguno de estos instrumentos:
1. Consentimiento expreso del titular.
2. Excepción del artículo 12 (no aplicable a los casos típicos de un proveedor de nube o
   inferencia).
3. Cláusulas Contractuales Modelo: Disposición DNPDP 60/2016 (contratos modelo de cesión y
   de prestación de servicios) y Resolución AAIP 198/2023 (cláusulas modelo de la RIPD,
   Responsable/Responsable y Responsable/Encargado). Si el contrato difiere de los modelos,
   el responsable debe solicitar aprobación de la AAIP dentro de los 30 días.
4. Normas Corporativas Vinculantes (Resolución AAIP 159/2018) para empresas de un mismo
   grupo económico.

Además, la Argentina aprobó el Convenio 108 del Consejo de Europa mediante la Ley 27.483,
lo que forma parte del marco de transferencias.

Fuentes:
- AAIP, "Transferencias internacionales" (acceso 2026-10-01).
- Resolución AAIP 198/2023: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-198-2023-391538/texto (acceso 2026-10-01).
- Resolución AAIP 159/2018: https://www.argentina.gob.ar/normativa/nacional/317228/texto (acceso 2026-10-01).
- Ley 27.483 (aprobación del Convenio 108): https://www.argentina.gob.ar/normativa/nacional/318245/texto (acceso 2026-10-01, referida desde la AAIP).

Nivel de certeza: ALTO. Nota: la AAIP exige consentimiento expreso como base, y la
interpretación de si el consentimiento abre la transferencia sin contrato se apoya en la
página oficial; conviene tratarla como criterio de la autoridad.

### 5.3 Adecuación de la Unión Europea respecto de Argentina

La Comisión Europea reconoce a Argentina como país con nivel adecuado de protección. La
decisión original es la Decisión 2003/490/CE (30 de junio de 2003). En enero de 2024 la
Comisión publicó el informe de la primera revisión periódica de las once decisiones de
adecuación adoptadas al amparo de la Directiva 95/46/CE, que incluye a Argentina, y la AAIP
informó que la Comisión "revalidó" el estatus. A la fecha de acceso, la Comisión Europea
sigue listando a Argentina entre los países adecuados, con enlace a la Decisión 2003/490/CE.

Fuentes:
- Comisión Europea, "Adequacy decisions": https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en (acceso 2026-10-01).
- Decisión 2003/490/CE: https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A32003D0490 (acceso 2026-10-01).
- AAIP, nota "Argentina logró la nueva adecuación por parte de la Unión Europea" (enero 2024), referida en https://www.argentina.gob.ar/transferencias-internacionales (acceso 2026-10-01).

Nivel de certeza: ALTO.

### 5.4 Distinción clave

La adecuación opera en dos direcciones y no debe confundirse:
- UE -> Argentina: Argentina es país adecuado para la UE (Decisión 2003/490/CE).
- Argentina -> EE. UU.: Estados Unidos no es país adecuado para Argentina; se requiere
  consentimiento o cláusulas contractuales modelo.

---

## 6. Sanciones

### 6.1 Administrativas

El artículo 31 faculta al órgano de control a aplicar apercibimiento, suspensión, multa de
mil pesos ($ 1.000) a cien mil pesos ($ 100.000), clausura o cancelación del archivo,
registro o banco de datos, sin perjuicio de responsabilidades administrativas, del
resarcimiento por daños y perjuicios y de las sanciones penales. La reglamentación debe
graduar las sanciones según gravedad y extensión.

Observación: los montos son nominales de la ley de 2000 y no se actualizan automáticamente.
Los proyectos de reforma de 2025 proponen una "unidad móvil" con valor inicial de
AR$ 100.000 y actualización semestral.

Fuente: Ley 25.326, art. 31; Bruchou & Funes de Rioja (9 de junio de 2025).

Nivel de certeza: ALTO sobre el texto; MEDIO sobre la afirmación de que no existe un
mecanismo de actualización vigente (no se verificó una norma de indexación).

### 6.2 Penales

El artículo 32 incorpora al Código Penal:
- Artículo 117 bis: inserción o difusión a sabiendas de datos falsos en un archivo de datos
  personales (prisión de un mes a dos años, con agravantes).
- Artículo 157 bis: acceso ilegítimo a un banco de datos personales o revelación de
  información registrada cuyo secreto se está obligado a preservar (prisión de un mes a dos
  años; inhabilitación especial de uno a cuatro años si el autor es funcionario público).

Fuente: Ley 25.326, art. 32 (texto InfoLEG).

Nivel de certeza: ALTO.

### 6.3 Régimen del Registro Nacional No Llame

La Ley 26.951 crea el Registro Nacional No Llame y su propio régimen sancionatorio. La AAIP
publica un Registro de Infractores de las leyes 25.326 y 26.951. No se verificaron en esta
investigación los montos sancionatorios de la Ley 26.951.

Fuentes:
- AAIP, "Registro de Infractores": https://www.argentina.gob.ar/quienes-no-cumplen-con-la-ley-de-proteccion-de-datos-personales-y-el-registro-no-llame (referida desde https://www.argentina.gob.ar/aaip/datospersonales, acceso 2026-10-01).

Nivel de certeza: MEDIO.

---

## 7. Novedades 2025-2026 relevantes

### 7.1 Decisiones automatizadas y derecho a la explicación

La Resolución AAIP 4/2019 (BO 16-01-2019) establece criterios de observancia obligatoria.
Su artículo 1 dispone la aplicación obligatoria y su anexo reconoce que, cuando el
responsable toma una decisión basada ÚNICAMENTE en tratamiento automatizado de datos y esta
produce efectos jurídicos perjudiciales o una afectación negativa significativa, el titular
puede solicitar al responsable una explicación de la lógica aplicada.

Además, el artículo 20 de la Ley 25.326 dispone que las decisiones judiciales o actos
administrativos que impliquen valoración de conductas humanas no pueden fundarse
únicamente en el resultado del tratamiento informatizado que defina el perfil o la
personalidad del interesado; los actos contrarios son nulos.

Esta base es relevante para un clasificador automático de incidentes: el sistema no decide
derechos sustanciales, pero la organización debería poder explicar la lógica de la
clasificación y ofrecer revisión humana.

Fuentes:
- Resolución AAIP 4/2019, artículo 1 y anexo (acceso 2026-10-01).
- Ley 25.326, art. 20 (texto InfoLEG).
- Mundo IA, 25 de septiembre de 2026 (síntesis del alcance acotado del art. 20 y de la
  Resolución 4/2019).

Nivel de certeza: ALTO sobre los textos citados; MEDIO sobre las interpretaciones de alcance
de la nota periodística.

### 7.2 Programas y guías de la AAIP sobre IA

- Resolución AAIP 161/2023 creó el Programa Nacional de Transparencia y Protección de Datos
  Personales en el uso de la Inteligencia Artificial (publicada en septiembre de 2023).
- La AAIP publica una "Guía para entidades públicas y privadas en materia de Transparencia y
  Protección de Datos Personales para una Inteligencia Artificial responsable". Una copia
  alojada en el repositorio de la OCDE indica "Buenos Aires, junio de 2024"; el sitio de la
  AAIP referencia además un archivo "guia_ai-final-2025.pdf".
- Resolución AAIP 145/2025 (BO 4 de agosto de 2025) creó el "Programa de Fortalecimiento de
  Protección de Datos Personales en la Administración Pública Nacional" (alcance: sector
  público).

Fuentes:
- AAIP, "Documentos de Inteligencia Artificial": https://www.argentina.gob.ar/aaip/documentos-de-inteligencia-artificial (acceso 2026-10-01).
- Copia OECD.AI de la guía (junio 2024): https://api.oecdai.org/storage/policy-initiatives/Jul2025/fu_ajw2gqk6mu7tnp4.pdf (acceso 2026-10-01).
- Portal Nacional de Transparencia (Resolución 161/2023): https://portal.transparencia.gob.ar/transparencia/transparenciaAlgoritmica (acceso 2026-10-01).
- Resolución AAIP 145/2025 (InfoLEG id 415899): https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=415899 (acceso 2026-10-01).

Nivel de certeza: ALTO sobre la existencia de los actos; MEDIO sobre la fecha exacta de la
versión vigente de la guía de IA.

### 7.3 Normas sectoriales y del sector público (2025-2026)

Según el relevamiento de septiembre de 2026 (fuente periodística que cita textos oficiales):
- BCRA: requisitos mínimos de gestión de riesgos tecnológicos con apartado específico de IA
  (texto ordenado al 13 de febrero de 2026; Comunicación A 8401), y "Guía de supervisión
  sobre el uso responsable y seguro de inteligencia artificial" (junio de 2026). Alcanza a
  entidades financieras, infraestructuras de pago sistémicas y proveedores de servicios de
  pago.
- SIGEN: Resolución 197/2026 (aprobada el 16 y publicada el 22 de junio de 2026), guía de
  controles de IA aplicable a todo el Sector Público Nacional.
- Ministerio Público Fiscal: Resolución PGN 64/2026 (septiembre de 2026), que prohíbe
  ingresar información reservada, causas en trámite y datos personales o sensibles en
  herramientas de IA de acceso público.
- Provincia de Buenos Aires: Resolución 4/2025 (14 de febrero de 2025), directrices para el
  uso de IA generativa por el personal de la administración provincial.
- Provincia de Santa Fe: Decreto 2726/2025 y Ley 14.428 (publicada el 26 de diciembre de
  2025), con exigencias de norma habilitante y revisión humana para sistemas automatizados.
  La Constitución provincial de 2025 reconoce el derecho a conocer criterios de decisiones
  algorítmicas.

Fuente: Mundo IA, 25 de septiembre de 2026 (con enlaces a los textos oficiales).

Nivel de certeza: MEDIO. Se verificó la existencia y el contenido general a través de una
fuente secundaria que cita los instrumentos; no se descargó ni verificó cada texto oficial.

### 7.4 Pseudonimización

No se identificó una norma argentina específica que regule la pseudonimización como técnica.
La Ley 25.326 define "disociación de datos" (art. 2) como el tratamiento que impide asociar
la información a persona determinada o determinable, y el artículo 11, inciso 3, apartado e,
exime de consentimiento la cesión cuando se aplicó un procedimiento de disociación. La
pseudonimización (datos que aún permiten reidentificación con información adicional) no está
expresamente legislada en la ley vigente; el concepto de "dato inferido" aparece en el
proyecto de reforma de 2025.

Fuentes: Ley 25.326, arts. 2 y 11; proyecto Carro 1948-D-2025.

Nivel de certeza: ALTO sobre la ausencia de regulación expresa de pseudonimización en el
texto vigente.

---

## 8. Implicancias para el sistema de mesa de ayuda (análisis)

Las siguientes son consecuencias operativas derivadas de las fuentes anteriores, no
conclusiones jurídicas vinculantes:

1. Registro de la base de datos: si el sistema conserva el directorio de empleados y los
   incidentes, corresponde evaluar la inscripción en el Registro Nacional de Bases de Datos
   Personales (Ley 25.326, arts. 21 y 24).
2. Transferencia a Gemini y Twilio (EE. UU.): Estados Unidos no es país adecuado. La
   organización debería apoyarse en cláusulas contractuales modelo (Disposición 60/2016 o
   Resolución 198/2023) o consentimiento expreso, y documentar el análisis. La
   pseudonimización previa mitiga el riesgo, pero no sustituye el instrumento de
   transferencia.
3. Brechas: al no existir una obligación general en la ley vigente, la organización no está
   legalmente obligada a notificar a la AAIP bajo la Ley 25.326, pero sería prudente adoptar
   el estándar de los proyectos (72 horas) por si se sanciona la reforma.
4. Decisiones automatizadas: la clasificación de incidentes no constituye una decisión
   judicial o administrativa del artículo 20, pero la Resolución AAIP 4/2019 fija el
   criterio de explicabilidad para decisiones exclusivamente automatizadas con efecto
   significativo. Conviene mantener la revisión humana y la trazabilidad ya previstas.
5. Plazos ARCO: corregir en la tesis el plazo de rectificación/supresión a CINCO DÍAS
   HÁBILES (art. 16), no corridos.
6. Consentimiento e información: la base de licitud de los empleados puede encuadrarse en el
   artículo 5, inciso 2, apartados b) o d) (obligación legal / relación laboral), pero el
   deber de información del artículo 6 subsiste.

---

## No verificado

Los siguientes puntos no pudieron confirmarse con fuentes primarias en esta investigación:

1. Fecha exacta y número de Boletín Oficial de publicación de la Ley 25.326.
2. Que exista una norma de actualización/indexación vigente de los montos de multa del
   artículo 31 de la Ley 25.326.
3. Montos y artículo exacto del régimen sancionatorio de la Ley 26.951 (Registro No Llame).
4. Identidad de todas las resoluciones de la AAIP emitidas entre 2025 y 2026 distintas de
   las citadas (Resoluciones 145/2025 y 161/2023), que pudieran afectar al sector privado.
5. Números exactos de las normas sectoriales de reporte de incidentes (por ejemplo, BCRA y
   telecomunicaciones).
6. Contenido íntegro del proyecto de Yeza (2025) y del expediente S-0644/2025: solo se
   accedió a resúmenes de fuentes secundarias.
7. Sanción de cualquier ley de reforma integral, de IA o de transparencia algorítmica:
   no se verificó ninguna sanción; los expedientes citados son proyectos.
8. Existencia de una resolución administrativa de la AAIP que imponga notificación de
   brechas al sector privado.
9. Fecha exacta de la versión vigente de la "Guía de IA" de la AAIP (junio de 2024 según
   copia OCDE; existencia de archivo 2025 en el sitio oficial).

---

## Fuentes consultadas (fecha de acceso: 2026-10-01)

Normativa y organismos:
- InfoLEG, Ley 25.326: http://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/norma.htm
- AAIP, Protección de datos personales: https://www.argentina.gob.ar/aaip/datospersonales
- AAIP, Obligaciones de los responsables: https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones
- AAIP, Transferencias internacionales: https://www.argentina.gob.ar/transferencias-internacionales
- AAIP, Proyecto de Ley de Protección de Datos Personales: https://www.argentina.gob.ar/aaip/datospersonales/proyecto-ley-datos-personales
- AAIP, Documentos de Inteligencia Artificial: https://www.argentina.gob.ar/aaip/documentos-de-inteligencia-artificial
- Resolución AAIP 4/2019: https://www.argentina.gob.ar/normativa/nacional/resolucion-4-2019-318874/texto
- Resolución AAIP 47/2018 (Boletín Oficial): https://www.boletinoficial.gob.ar/detalleAviso/primera/188654/20180725
- Resolución AAIP 159/2018: https://www.argentina.gob.ar/normativa/nacional/317228/texto
- Resolución AAIP 198/2023: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-198-2023-391538/texto
- Disposición DNPDP 60/2016: https://www.argentina.gob.ar/sites/default/files/disp_e2016_60.pdf
- Resolución AAIP 145/2025 (InfoLEG): https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=415899
- Ley 27.483 (Convenio 108): https://www.argentina.gob.ar/normativa/nacional/318245/texto

Proyectos de ley (PDF descargados del Congreso):
- Mensaje 87/2023: https://www.argentina.gob.ar/sites/default/files/mensajeyproyecto_leypdp2023.pdf
- 1948-D-2025 (Carro): https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2025/PDF2025/TP2025/1948-D-2025.pdf
- 3540-D-2025 (transparencia algorítmica): https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2025/PDF2025/TP2025/3540-D-2025.pdf
- 2968-D-2025 (niñas, niños y adolescentes): https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2025/PDF2025/TP2025/2968-D-2025.pdf

Unión Europea:
- Comisión Europea, Adequacy decisions: https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en
- Decisión 2003/490/CE: https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A32003D0490

Análisis jurídico y prensa especializada:
- Bruchou & Funes de Rioja, 9 de junio de 2025: https://bruchoufunes.com/proteccion-de-datos-personales-se-presento-un-nuevo-proyecto-de-ley-en-la-camarade-diputados/
- Abogados.com.ar, 25 de junio de 2025: https://abogados.com.ar/proteccion-de-datos-personales-propuesta-de-ley/37067
- Mundo IA, 25 de septiembre de 2026: https://www.mundoia.com.ar/regulacion-inteligencia-artificial-argentina-reglas-vigentes/
