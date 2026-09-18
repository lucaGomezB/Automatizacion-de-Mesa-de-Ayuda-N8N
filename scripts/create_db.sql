-- create_db.sql — helper manual para crear el rol y la base en una instancia
-- PostgreSQL ya existente.
--
-- Uso:
--   psql -v db_password="<password>" -f scripts/create_db.sql
--
-- La password debe coincidir con POSTGRES_PASSWORD del docker-compose / .env
-- raiz. No se hardcodea ninguna credencial en este archivo (repo publico); si
-- se omite -v db_password, psql aborta con un error explicito.

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'mesa') THEN
    EXECUTE format('CREATE ROLE mesa WITH LOGIN PASSWORD %L', :'db_password');
  END IF;
END
$$;

CREATE DATABASE mesa_de_ayuda OWNER mesa;

\c mesa_de_ayuda
GRANT ALL PRIVILEGES ON DATABASE mesa_de_ayuda TO mesa;
GRANT ALL ON SCHEMA public TO mesa;
