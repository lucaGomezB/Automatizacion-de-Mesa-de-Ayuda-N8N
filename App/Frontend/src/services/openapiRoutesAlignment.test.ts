/**
 * Seam FE 2: las rutas HTTP que arma el cliente deben coincidir exactamente
 * con las rutas declaradas en la especificacion OpenAPI (docs/openapi.json),
 * incluyendo el trailing slash.
 *
 * Defecto que expone: el cliente llama a `/incidentes` (y `api.ts` agrega el
 * prefijo `/api/v1`), pero la especificacion declara `/api/v1/incidentes/`.
 * El desajuste deriva en 307/404 segun el proxy que este delante.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { readFileSync } from 'node:fs';
import path from 'node:path';

// Mockear el modulo completo de api para controlar apiClient (mismo patron que
// incidentesService.test.ts).
vi.mock('./api', async (importOriginal) => {
  const original = await importOriginal<typeof import('./api')>();
  return {
    ...original,
    apiClient: {
      post: vi.fn(),
      get: vi.fn(),
      patch: vi.fn(),
    },
  };
});

import { apiClient } from './api';
import { listarIncidentes } from './incidentesService';

const mockedApiClient = vi.mocked(apiClient);

// El prefijo que api.ts concatena a VITE_API_BASE_URL al construir baseURL.
const API_PREFIX = '/api/v1';

// docs/openapi.json vive en la raiz del repo; `npm run test` corre desde
// App/Frontend, por lo que el archivo queda en '../../docs/openapi.json'.
const OPENAPI_PATH = path.resolve(process.cwd(), '..', '..', 'docs', 'openapi.json');

interface OpenApiDocument {
  paths: Record<string, unknown>;
}

const openapiPaths = new Set(
  Object.keys(
    (JSON.parse(readFileSync(OPENAPI_PATH, 'utf-8')) as OpenApiDocument).paths,
  ),
);

describe('alineacion de rutas del cliente con OpenAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('la ruta de listar incidentes coincide exactamente con la ruta OpenAPI', async () => {
    vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [] });

    await listarIncidentes();

    const clientPath = vi.mocked(mockedApiClient.get).mock.calls[0]?.[0] as string;
    const fullPath = `${API_PREFIX}${clientPath}`;
    const candidatos = [...openapiPaths].filter(
      (p) => p === fullPath || p === `${fullPath}/`,
    );

    expect(
      openapiPaths.has(fullPath),
      `El cliente llama '${fullPath}' pero OpenAPI declara ` +
        `${JSON.stringify(candidatos)}; hay desalineacion de trailing slash.`,
    ).toBe(true);
  });
});
