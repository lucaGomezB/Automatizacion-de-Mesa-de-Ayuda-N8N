/**
 * Contenido de la politica de privacidad (c-66, PRIV-002).
 *
 * Se extrae del componente para que sea testeable de forma aislada y para
 * versionar el texto editorial en un unico lugar. El componente `Privacidad`
 * solo se encarga de presentarlo.
 *
 * Regla de lenguaje: usa "alineado con" y NO afirma certificacion, conformidad
 * ni cumplimiento (terminos prohibidos: "certificado", "compliant", "cumple").
 */

export interface SeccionPrivacidad {
  /** Titulo de la seccion. */
  titulo: string;
  /** Parrafos de la seccion, en orden. */
  parrafos: string[];
}

export const TITULO_PRIVACIDAD = 'Politica de Privacidad';

export const INTRO_PRIVACIDAD =
  'Este aviso describe como el Sistema de Automatizacion de Mesa de Ayuda trata ' +
  'los datos personales, alineado con la Ley 25.326 de Proteccion de Datos ' +
  'Personales de la Republica Argentina.';

export const SECCIONES_PRIVACIDAD: SeccionPrivacidad[] = [
  {
    titulo: 'Finalidad del tratamiento',
    parrafos: [
      'Los datos personales se tratan con la finalidad de registrar, clasificar y ' +
        'resolver los incidentes reportados, y de gestionar la mesa de ayuda.',
    ],
  },
  {
    titulo: 'Responsable del tratamiento',
    parrafos: [
      'El responsable es la organizacion adoptante del sistema, a traves de su ' +
        'funcion de proteccion de datos.',
    ],
  },
  {
    titulo: 'Destinatarios de los datos',
    parrafos: [
      'Los datos pueden comunicarse a los proveedores de infraestructura y de ' +
        'inteligencia artificial que prestan servicios al sistema, y al personal ' +
        'autorizado de la mesa de ayuda.',
    ],
  },
  {
    titulo: 'Bases de licitud',
    parrafos: [
      'El tratamiento se sustenta en el consentimiento del titular al reportar un ' +
        'incidente y en el interes legitimo de la organizacion en gestionar sus ' +
        'servicios.',
    ],
  },
  {
    titulo: 'Transferencia internacional',
    parrafos: [
      'Los datos se transfieren a proveedores con sede en Estados Unidos: Gemini ' +
        '(clasificacion y transcripcion de audio) y Twilio (telefonia). Estados ' +
        'Unidos no es un pais con nivel adecuado de proteccion; la transferencia se ' +
        'ampara en el consentimiento expreso del titular o en clausulas ' +
        'contractuales modelo. La pseudonimizacion mitiga el riesgo pero no ' +
        'sustituye el instrumento de transferencia.',
    ],
  },
  {
    titulo: 'Derechos del titular y plazos',
    parrafos: [
      'El titular puede ejercer los derechos de acceso, rectificacion, ' +
        'actualizacion y supresion. El derecho de acceso se responde dentro de los ' +
        '10 dias corridos. La rectificacion, actualizacion y supresion se responden ' +
        'dentro de los 5 dias habiles.',
    ],
  },
  {
    titulo: 'Canal para ejercer los derechos',
    parrafos: [
      'Las solicitudes se presentan por el canal informado por la funcion de ' +
        'proteccion de datos de la organizacion adoptante, conforme al ' +
        'procedimiento ARCO documentado por la organizacion.',
    ],
  },
];

export const ADVERTENCIA_RESPUESTAS_AUTOMATICAS =
  'Algunas notificaciones del sistema generan respuestas automaticas.';
