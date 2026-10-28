# Inventario de dependencias y licencias

> **Control mapeado**: ISO/IEC 27002:2022 5.32 (Propiedad intelectual); NIST CSF 2.0 GV.
> Requisito SGD-020.
> **Estado**: v1 — aprobada por el autor el 2026-10-28 (governance MEDIO).
> **Alcance**: dependencias principales de backend (`App/Backend/requirements.txt`) y frontend
> (`App/Frontend/package.json`), su licencia declarada y las obligaciones de atribucion.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. La verificacion legal definitiva compete a la organizacion
> adoptante.

## 1. Proposito

Identificar las dependencias de software de terceros y su licencia declarada, como base del
control de propiedad intelectual (5.32). Este documento es un **inventario de referencia**; la
licencia efectiva de cada paquete es la de su propio repositorio y archivo de licencia, y la
verificacion legal definitiva corresponde a la organizacion adoptante. El inventario **no
contiene credenciales ni secretos**.

## 2. Dependencias de backend

`App/Backend/requirements.txt`.

| Dependencia | Rol | Licencia declarada | Obligacion |
|-------------|-----|--------------------|------------|
| fastapi | Framework web | MIT | Atribucion (conservar aviso de copyright) |
| starlette | Framework ASGI | BSD-3-Clause | Atribucion |
| uvicorn | Servidor ASGI | BSD-3-Clause | Atribucion |
| python-multipart | Parseo de formularios | Apache-2.0 | Atribucion y aviso de cambios |
| asyncpg | Driver PostgreSQL | Apache-2.0 | Atribucion y aviso de cambios |
| sqlalchemy | ORM | MIT | Atribucion |
| alembic | Migraciones | MIT | Atribucion |
| pydantic | Validacion de datos | MIT | Atribucion |
| pydantic-settings | Configuracion | MIT | Atribucion |
| google-genai | Cliente Google Gemini | Apache-2.0 | Atribucion y aviso de cambios |
| httpx | Cliente HTTP | BSD-3-Clause | Atribucion |
| structlog | Logging estructurado | MIT / Apache-2.0 (dual) | Atribucion |
| cryptography | Fernet y primitivas | Apache-2.0 / BSD-3-Clause (dual) | Atribucion y aviso de cambios |
| python-jose | JWT | MIT | Atribucion |
| bcrypt | Hashing de contrasenas | Apache-2.0 | Atribucion |
| pyotp | TOTP (RFC 6238) | MIT | Atribucion |

Dependencias de desarrollo y prueba: `pytest` (MIT), `pytest-asyncio` (Apache-2.0),
`aiosqlite` (MIT), `pytest-cov` (MIT) y `coverage` (Apache-2.0). No se distribuyen en el
artefacto de produccion.

## 3. Dependencias de frontend

`App/Frontend/package.json`.

| Dependencia | Rol | Licencia declarada | Obligacion |
|-------------|-----|--------------------|------------|
| react / react-dom | Biblioteca de UI | MIT | Atribucion |
| react-router-dom | Enrutado | MIT | Atribucion |
| @tanstack/react-query | Estado de servidor | MIT | Atribucion |
| @radix-ui/react-* | Primitivas de UI | MIT | Atribucion |
| axios | Cliente HTTP | MIT | Atribucion |
| react-hook-form | Formularios | MIT | Atribucion |
| recharts | Graficos | MIT | Atribucion |
| html2canvas | Captura de DOM | MIT | Atribucion |
| lucide-react | Iconografia | ISC | Atribucion |
| class-variance-authority | Variantes de estilo | Apache-2.0 | Atribucion y aviso de cambios |
| clsx / tailwind-merge | Utilidades de clases | MIT | Atribucion |
| tailwindcss | Framework de estilos | MIT | Atribucion |

Dependencias de desarrollo: `typescript` (Apache-2.0), `vite` (MIT), `vitest` (MIT),
`eslint` y plugins (MIT), `@testing-library/*` (MIT), `happy-dom` (MIT), `postcss` (MIT) y
`@vitejs/plugin-react` (MIT).

## 4. Obligaciones y copyleft

- **Licencias permisivas**: todas las dependencias principales listadas usan licencias
  permisivas (MIT, BSD-3-Clause, Apache-2.0, ISC). **No se identifico ninguna dependencia
  con licencia copyleft fuerte** (GPL, AGPL, LGPL) que imponga la liberacion del codigo del
  proyecto.
- **Atribucion**: las licencias MIT, BSD e ISC exigen conservar el aviso de copyright y el
  texto de licencia. En un artefacto distribuido, la organizacion adoptante debe incluir el
  aviso de terceros correspondiente.
- **Apache-2.0**: ademas de la atribucion, exige indicar los cambios realizados sobre el
  paquete (no aplica si el paquete se usa sin modificar) y conservar el aviso `NOTICE` cuando
  el paquete lo declare.
- **Verificacion**: el inventario es de referencia. La organizacion adoptante debe validar la
  licencia efectiva de cada dependencia (incluidas las transitivas) antes de distribuir el
  sistema fuera del alcance de la tesis.

## 5. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.32 y NIST CSF 2.0 GV. No constituye
certificacion ni auditoria. La verificacion legal definitiva de las licencias corresponde a la
organizacion adoptante.
