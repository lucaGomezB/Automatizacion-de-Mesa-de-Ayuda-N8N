# Fuentes de terceros

Carpeta para depositar papers, PDFs y documentos de **terceros** (con copyright) que se
descargan solo para su revision local durante la tesis. Ejemplo: el texto completo de un
trabajo citado cuando el resumen no alcanza para verificar una cifra.

## Reglas

- **NUNCA se versiona** el contenido de esta carpeta. El repositorio es publico y estos
  documentos tienen copyright (IEEE, Springer, arXiv, etc.). Solo se versiona este `README.md`
  (ver la regla correspondiente en `.gitignore`).
- El contenido se descarga bajo el acceso legitimo del autor: acceso abierto, acceso
  institucional, o copia provista por el autor. No se publica ni se redistribuye.
- Cuando un dato de la tesis se verifica contra una de estas fuentes, se consigna la
  procedencia en el texto (cita con DOI/URL) y, si corresponde, en `docs/Tesis/Correcciones/`
  con la metrica verificada; **el PDF en si no se versiona**.
- Nombres sugeridos: `<clave_bib>.pdf` (por ejemplo `Paramesh2019_it_service_desk.pdf` o
  `paket2024itservice.pdf`), para que la trazabilidad sea trivial.

## Estado

- `2103.15822v1.pdf`: depositado el 2026-11-22 y usado para verificar (c-247, tarea 5.4) las
  cifras del companero de arXiv: 10.742 tickets, 18 clases, particion 70:30 y exactitud maxima
  de 92,04 % con bagging. Todas coinciden con el texto de la tesis.
