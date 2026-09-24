# Guia: crear una API key de Gemini con creditos prepagos

Documento para compartir con los integrantes del grupo. Explica como crear una
API key de Google Gemini con creditos prepagos en una cuenta propia y como
compartirla con el equipo del proyecto.

## Objetivo

Obtener una **API key de Gemini** con **creditos prepagos (~USD 10)** en la
cuenta de quien la cree, para que el grupo la use en el backend del proyecto.
Quien paga mantiene el control del gasto; el equipo solo consume la key.

## Requisitos

- Cuenta de Google.
- Una **tarjeta de credito** (Visa, Mastercard o Amex).
  - **No sirve tarjeta prepaga** (Uala, Mercado Pago, etc.): Google las rechaza
    por politica.
  - Tarjeta de **debito**: puede servir solo si soporta pagos recurrentes y no
    exige 2FA por SMS. Si da error, usar tarjeta de credito.

## Parte 1 - Crear la API key

1. Entrar a `https://aistudio.google.com/app/apikey` con la cuenta de Google.
2. Aceptar los terminos si es la primera vez.
3. Clic en **Create API key**.
4. Elegir un **proyecto de Google Cloud** existente o dejar que cree uno nuevo.
5. Copiar la key generada. Empieza con `AQ.`. Guardarla en un lugar seguro.

## Parte 2 - Cargar creditos prepagos (minimo USD 10)

6. Entrar a `https://aistudio.google.com/billing`.
7. Clic en **Set up Billing** / **Upgrade to paid tier**.
8. La consola redirige a **Google Cloud** para crear o vincular una cuenta de
   facturacion (nombre, pais, moneda).
9. Agregar la **tarjeta de credito** como metodo de pago.
10. Elegir la opcion de **creditos prepagos** y cargar el **minimo de USD 10**.
11. **Importante:** dejar **auto-reload (recarga automatica) DESACTIVADO**. Si se
    desea, fijar el **Monthly Auto-Charge Limit** al minimo. Asi el gasto maximo
    es exactamente lo cargado, sin cargos sorpresa.
12. Confirmar la compra.

## Parte 3 - Verificar

13. Volver a AI Studio y confirmar que el proyecto figura en **Paid tier**.
14. (Opcional) Probar la key con una consulta simple.

## Parte 4 - Compartir la key con el grupo (de forma segura)

15. Enviar la key por un **canal privado**: mensaje directo o, mejor, un gestor
    de contrasenas (Bitwarden, 1Password) con enlace de un solo uso.
16. **No** publicarla en un grupo publico, ni en un repositorio, ni en un issue.
    Una API key es una credencial: quien la tenga puede gastar los creditos.
17. Si se sospecha una filtracion, revocarla/regenerarla desde
    `https://aistudio.google.com/app/apikey`.

## Que hace el equipo con la key

- La guarda en `App/Backend/.env`, que esta **ignorado por git**.
- **No** la commitea ni la incluye en el repositorio.
- La usa solo para clasificar incidentes y transcribir audio (STT).

## Recordatorios para quien paga

- La **exposicion maxima es lo que cargue** (USD 10), porque auto-reload queda
  apagado.
- Opcional: en Google Cloud -> Billing se puede configurar una **alerta de
  presupuesto** (notifica; no corta el servicio por si sola).

## Plan B de costo cero (opcional, con advertencia)

Si ningun integrante consigue tarjeta de credito, cada miembro puede crear su
propia key **gratuita** y repartir el corpus entre varias (el free tier da 20
requests/dia **por proyecto**). Con 3 integrantes serian ~60/dia. **Advertencia:**
usar varias cuentas a proposito para esquivar el limite de cuota puede ir contra
los terminos de Google; por eso es un plan B, no el recomendado. El camino limpio
sigue siendo la key paga de USD 10.

## Cierre: que hacer cuando llega la key

1. Cargarla en `App/Backend/.env` (linea `GEMINI_API_KEY=`).
2. Recrear el backend: `docker compose up -d --force-recreate backend`.
3. Verificar que responda sin error 429 (paid tier) y correr el smoke test del
   clasificador.

## Referencias

- API keys: `https://aistudio.google.com/app/apikey`
- Billing de AI Studio: `https://aistudio.google.com/billing`
- Politica de metodos de pago de Google Cloud:
  `https://cloud.google.com/billing/docs/how-to/payment-methods`