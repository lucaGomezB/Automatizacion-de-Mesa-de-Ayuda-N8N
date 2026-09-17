## ADDED Requirements

### Requirement: Build de Docker propaga VITE_API_BASE_URL

La build de Docker del frontend SHALL propagar la variable `VITE_API_BASE_URL` en tiempo de compilacion, de modo que el bundle resultante use el valor provisto por el entorno de despliegue y MUST NOT quede fijado a una URL hardcodeada. El proceso de build SHALL fallar o advertir explicitamente si la variable falta cuando es requerida.

#### Scenario: La build usa el valor provisto

- **WHEN** se construye la imagen del frontend con `VITE_API_BASE_URL` definido
- **THEN** el bundle incluye ese valor y las llamadas del cliente lo usan

#### Scenario: Sin la variable no queda una URL hardcodeada silenciosa

- **WHEN** se construye la imagen sin `VITE_API_BASE_URL`
- **THEN** el build no produce un bundle que apunte a una URL hardcodeada distinta de la documentada

### Requirement: Volumenes de hot-reload coherentes con lo ejecutado

En el entorno de desarrollo en Docker, los volumenes montados para hot-reload SHALL corresponder al codigo que el proceso efectivamente ejecuta. Un volumen que monte una ruta que el proceso no usa MUST considerarse un defecto de configuracion.

#### Scenario: El codigo editado es el que corre

- **WHEN** se edita un archivo de codigo fuente del frontend o backend en el entorno de desarrollo
- **THEN** el proceso en el contenedor refleja el cambio, porque el volumen montado coincide con la ruta ejecutada

#### Scenario: Un volumen inutil es detectado como defecto

- **WHEN** se inspecciona la configuracion del entorno de desarrollo
- **THEN** no existe un volumen que monte una ruta distinta a la que el proceso ejecuta
