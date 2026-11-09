# Design: Aceptar la imagen derivada de N8N en el pin INFRA-008

## Contexto

c-182 reemplazo `image:` por `build:` en el servicio `n8n` (imagen derivada con un parche de
`@n8n/imap`). La base sigue pineada en `docker/n8n/Dockerfile` (`FROM n8nio/n8n:2.11.2`). El
guard de c-62 solo conocia la forma `image:`.

## Decisiones

- **D1 — El contrato es el pin de la base, no la forma de declararlo.** Se acepta `image ==
  n8nio/n8n:2.11.2` o `build` cuyo primer `FROM` sea esa imagen. No se relaja el pin: una
  version distinta o `latest` sigue fallando.
- **D2 — Funcion pura testeable.** `resolver_imagen_n8n(services, repo_root) -> str` devuelve
  la imagen efectiva ('' si no se resuelve: sin `image` ni `build`, o sin Dockerfile). Se
  testea con `tmp_path` sin tocar el compose real.
- **D3 — Primer `FROM`.** En multi-stage la base del servicio es la del primer `FROM`; el
  alias (`AS base`) y los flags (`--platform=...`) no forman parte de la imagen.
- **D4 — Sin cambios de infraestructura.** No se modifica el compose ni el Dockerfile
  (gobernanza ALTA de C-62): solo el guard y su spec.

## Riesgos

- Un `ARG` en el `FROM` (`FROM ${BASE}`) no se resuelve y el guard fallara de forma visible;
  es el comportamiento deseado (el pin debe ser literal).
