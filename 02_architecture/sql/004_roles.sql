-- Exemple de rôles PostgreSQL à adapter à l'environnement réel.
-- Ne pas exécuter avec les mots de passe ci-dessous en production.
CREATE ROLE luxury_stock_reader NOLOGIN;
CREATE ROLE luxury_stock_writer NOLOGIN;
GRANT USAGE ON SCHEMA luxury_stock TO luxury_stock_reader, luxury_stock_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA luxury_stock TO luxury_stock_reader;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA luxury_stock TO luxury_stock_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA luxury_stock GRANT SELECT ON TABLES TO luxury_stock_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA luxury_stock GRANT SELECT, INSERT, UPDATE ON TABLES TO luxury_stock_writer;
