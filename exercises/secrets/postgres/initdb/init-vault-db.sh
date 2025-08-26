#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER $VAULT_USER WITH PASSWORD '$VAULT_PASSWORD';
	CREATE DATABASE vault;
	GRANT ALL PRIVILEGES ON DATABASE vault TO $VAULT_USER;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER $TEST_USER WITH PASSWORD '$TEST_PASSWORD';
	CREATE DATABASE test;
	GRANT ALL PRIVILEGES ON DATABASE test TO $TEST_USER;
  ALTER ROLE $TEST_USER CREATEROLE;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "vault" <<-EOSQL
	CREATE TABLE vault_kv_store (
		parent_path TEXT COLLATE "C" NOT NULL,
		path        TEXT COLLATE "C",
		key         TEXT COLLATE "C",
		value       BYTEA,
		CONSTRAINT pkey PRIMARY KEY (path, key)
	);

	CREATE INDEX parent_path_idx ON vault_kv_store (parent_path);

	CREATE TABLE vault_ha_locks (
		ha_key                                      TEXT COLLATE "C" NOT NULL,
		ha_identity                                 TEXT COLLATE "C" NOT NULL,
		ha_value                                    TEXT COLLATE "C",
		valid_until                                 TIMESTAMP WITH TIME ZONE NOT NULL,
		CONSTRAINT ha_key PRIMARY KEY (ha_key)
	);

	GRANT ALL PRIVILEGES ON TABLE vault_ha_locks TO $VAULT_USER;
	GRANT ALL PRIVILEGES ON TABLE vault_kv_store TO $VAULT_USER;
EOSQL
