-- Rôles PostgreSQL, principe du moindre privilège.
-- Aucun mot de passe n'est écrit ici : ils sont lus dans l'environnement
-- (LUXURY_APP_PASSWORD, LUXURY_PIPELINE_PASSWORD, définis dans .env).
-- Script rejouable : les rôles existants sont conservés, leur mot de passe est mis à jour.
--
--   luxury_stock_reader      groupe, lecture seule (dashboard)
--   luxury_stock_writer      groupe, lecture + insertion + mise à jour (ingestion, prévisions)
--   luxury_stock_maintainer  groupe, lecture + mise à jour + suppression, à accorder
--                            temporairement à un compte nommé (droits des personnes, maintenance)
--   luxury_stock_app         connexion du dashboard, membre de reader
--   luxury_stock_pipeline    connexion du pipeline, membre de writer
\set ON_ERROR_STOP on
\getenv app_pw LUXURY_APP_PASSWORD
\getenv pipeline_pw LUXURY_PIPELINE_PASSWORD

\if :{?app_pw}
\else
    DO $$ BEGIN RAISE EXCEPTION 'LUXURY_APP_PASSWORD manquant (voir .env.example)'; END $$;
\endif
\if :{?pipeline_pw}
\else
    DO $$ BEGIN RAISE EXCEPTION 'LUXURY_PIPELINE_PASSWORD manquant (voir .env.example)'; END $$;
\endif

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_reader') THEN
        CREATE ROLE luxury_stock_reader NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_writer') THEN
        CREATE ROLE luxury_stock_writer NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_maintainer') THEN
        CREATE ROLE luxury_stock_maintainer NOLOGIN;
    END IF;
END $$;

SELECT format('CREATE ROLE luxury_stock_app LOGIN PASSWORD %L', :'app_pw')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_app') \gexec
SELECT format('ALTER ROLE luxury_stock_app PASSWORD %L', :'app_pw')
WHERE EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_app') \gexec
SELECT format('CREATE ROLE luxury_stock_pipeline LOGIN PASSWORD %L', :'pipeline_pw')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_pipeline') \gexec
SELECT format('ALTER ROLE luxury_stock_pipeline PASSWORD %L', :'pipeline_pw')
WHERE EXISTS (SELECT FROM pg_roles WHERE rolname = 'luxury_stock_pipeline') \gexec

GRANT luxury_stock_reader TO luxury_stock_app;
GRANT luxury_stock_writer TO luxury_stock_pipeline;
ALTER ROLE luxury_stock_app SET search_path = luxury_stock;
ALTER ROLE luxury_stock_pipeline SET search_path = luxury_stock;

-- Retirer les droits implicites accordés à PUBLIC
REVOKE ALL ON SCHEMA luxury_stock FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA luxury_stock FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

GRANT USAGE ON SCHEMA luxury_stock TO luxury_stock_reader, luxury_stock_writer, luxury_stock_maintainer;
GRANT SELECT ON ALL TABLES IN SCHEMA luxury_stock TO luxury_stock_reader;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA luxury_stock TO luxury_stock_writer;
GRANT SELECT, UPDATE, DELETE ON ALL TABLES IN SCHEMA luxury_stock TO luxury_stock_maintainer;

-- Mêmes droits pour les tables créées plus tard par le rôle qui exécute ce script
ALTER DEFAULT PRIVILEGES IN SCHEMA luxury_stock GRANT SELECT ON TABLES TO luxury_stock_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA luxury_stock GRANT SELECT, INSERT, UPDATE ON TABLES TO luxury_stock_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA luxury_stock GRANT SELECT, UPDATE, DELETE ON TABLES TO luxury_stock_maintainer;
