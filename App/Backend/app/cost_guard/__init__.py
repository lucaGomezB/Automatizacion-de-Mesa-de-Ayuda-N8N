"""
Guarda de costo en runtime (c-45-runtime-cost-guard).

Este paquete concentra el enforcement del gasto de las tres superficies pagas
(Gemini del backend, Gemini del AI Agent de n8n y transcripcion de Twilio) con
una bolsa global compartida, costo unitario por superficie y limites de tasa.
El almacen de contadores y el reloj se inyectan como protocolos, de modo que
la guarda es evaluable offline con fakes.
"""
