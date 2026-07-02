## Design: Corpus Simulado de 200 Casos

### D1: Estrategia de generacion

Se utiliza un script de generacion (`evaluation/generate_corpus.py`) con templates y placeholders en lugar de escribir 200 casos a mano. Esto permite:

- **Reproducibilidad**: seed fijo (42) garantiza el mismo output en cada ejecucion
- **Auditabilidad**: los templates son explicitos y revisables
- **Extensibilidad**: se pueden agregar variaciones sin editar 200 lineas

El script define ~30 templates por categoria con placeholders (`{server}`, `{sistema}`, `{persona}`, etc.) que se reemplazan aleatoriamente desde listas de valores realistas. Esto genera variacion natural sin depender de un LLM.

### D2: Distribucion y categorias

| Categoria | Cantidad | % | Sub-temas |
|-----------|----------|---|-----------|
| Sistemas | 82 | 41% | Servidores caidos, red sin conexion, VPN no funciona, base de datos lenta, permisos de acceso, instalacion de software, actualizaciones del sistema, errores de configuracion |
| Operaciones | 64 | 32% | Bloqueo de cuenta, reseteo de clave, problemas de login, alta/baja de empleados, solicitudes de acceso, errores en procesos batch, problemas con formularios del sistema |
| Soporte Tecnico | 54 | 27% | Impresora no imprime, PC no enciende, monitor fallado, teclado/mouse roto, telefono no funciona, problemas de cableado, equipo lento, pantalla azul |

### D3: Formato de cada caso

Cada incidente del corpus tiene:

- **descripcion**: 15-50 palabras en espanol rioplatense, con variedad de estilos (formal, informal, urgente, tecnico)
- **canal_origen**: distribuido realisticamente (correo 60%, formulario web 25%, telefono 15%)
- **categoria_real**: etiqueta ground truth (una de las tres categorias canonicas)
- **id**: secuencial de 1 a 200

### D4: Realismo linguistico

Para que el corpus sea util como proxy del corpus real:

1. **Variedad sintactica**: algunas descripciones son formales ("Por medio del presente solicito..."), otras informales ("Che, no me anda..."), otras tecnicas ("Error 500 en el endpoint /api/v1/...")
2. **Jerga local**: incluye terminos como "laburar", "puesto", "maquina", "pedido", "sistema de gestion", "permisos de carpeta"
3. **Errores de tipeo (~10%)**: "nesecito" en vez de "necesito", "hayuda" en vez de "ayuda", "conecsion" en vez de "conexion", omision de tildes en algunas palabras
4. **Distribucion de longitud**: ~10% cortas (10-15 palabras), ~50% medias (15-30), ~40% largas (30-50 palabras)
5. **Casos borde**: descripciones ambiguas que mezclan categorias, casos con solo jerga tecnica, casos con solo queja no tecnica

### D5: Pseudonimizacion

Todos los datos son simulados. Se usan:

- **Nombres**: placeholder (Juan Perez, Maria Garcia, Carlos Lopez, etc.)
- **Emails**: formato valido pero fake (usuario@empresa.com.ar)
- **Telefonos**: formato Mendoza (+54 261 5XX-XXXX) pero numeros falsos
- **Nombres de sistemas**: genericos (ERP, SAP, Tango, Sistema de Gestion, CRM, Active Directory)
- **Nombres de servidores**: patron dummy (SRV-APP-01, srv-bbdd-02)

El archivo incluye una cabecera de comentario indicando "DATOS SIMULADOS — NO CONTIENE PII REAL" para prevenir usos incorrectos.

### D6: Columnas del CSV

```csv
id,descripcion,canal_origen,categoria_real
```

Nota: las columnas opcionales `tiempo_manual_s` y `tiempo_automatizado_s` NO se incluyen. Estas solo tienen sentido en el corpus real (mediciones cronometradas). El framework las maneja como opcionales sin error.

### D7: Script de generacion

Estructura del script:

```python
# evaluation/generate_corpus.py
import csv, random
random.seed(42)

# Templates por categoria con placeholders {var}
# ~30 templates por categoria = 90 templates total
# Cada template tiene 3-5 variantes de placeholder para generar diversidad

# Logica:
# 1. Para cada categoria, seleccionar N templates aleatoriamente (con reemplazo)
# 2. Completar placeholders con valores aleatorios
# 3. Aplicar transformaciones de realismo (~10% con errores de tipeo)
# 4. Asignar canal_origen segun distribucion 60/25/15
# 5. Escribir CSV con ids secuenciales

def generate_corpus(output_path):
    casos = []
    casos += generate_sistemas(82)
    casos += generate_operaciones(64)
    casos += generate_soporte_tecnico(54)
    random.shuffle(casos)
    # Asignar ids secuenciales
    write_csv(output_path, casos)
```

### D8: Validacion post-generacion

Despues de generar el CSV:

1. Verificar row count = 200
2. Verificar distribucion: Sistemas 82, Operaciones 64, Soporte Tecnico 54
3. Verificar que el framework carga el CSV sin errores: `cargar_corpus('data/corpus_evaluacion.csv')`
4. Verificar que pasa los tests de corpus existentes (categorias validas, columnas requeridas)
