DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'mesa') THEN
    CREATE ROLE mesa WITH LOGIN PASSWORD 'mesa';
  END IF;
END
$$;

CREATE DATABASE mesa_de_ayuda OWNER mesa;

\c mesa_de_ayuda
GRANT ALL PRIVILEGES ON DATABASE mesa_de_ayuda TO mesa;
GRANT ALL ON SCHEMA public TO mesa;
