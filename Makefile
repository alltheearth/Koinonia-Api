.PHONY: help build up down logs migrate secrets deploy rm-stack ps secrets-test deploy-test rm-stack-test ps-test

ENV_FILE ?= .env.docker
TEST_ENV_FILE ?= .env.test

help:
	@echo "make build        - builda as imagens koinonia-api (este repo) e shepherds-toolkit-api"
	@echo "make up           - sobe tudo localmente via docker compose (usa $(ENV_FILE))"
	@echo "make down         - derruba o docker compose local"
	@echo "make logs         - segue os logs do docker compose local"
	@echo "make migrate      - roda as migrations nos dois backends (compose local)"
	@echo "make secrets      - cria/atualiza os Docker secrets de PRODUCAO a partir de $(ENV_FILE)"
	@echo "make deploy       - builda as imagens e sobe o swarm-stack.yml (VPS producao)"
	@echo "make rm-stack     - remove o stack de producao do Swarm"
	@echo "make ps           - lista os servicos do stack de producao"
	@echo "make secrets-test - cria/atualiza os Docker secrets test_* a partir de $(TEST_ENV_FILE)"
	@echo "make deploy-test  - builda as imagens e sobe o swarm-stack.test.yml (notebook de teste)"
	@echo "make rm-stack-test - remove o stack de teste do Swarm"
	@echo "make ps-test      - lista os servicos do stack de teste"

build:
	docker build -t koinonia-api:latest .
	docker build -t shepherds-toolkit-api:latest ../shepherds-toolkit-api

up:
	docker compose --env-file $(ENV_FILE) up -d --build

down:
	docker compose --env-file $(ENV_FILE) down

logs:
	docker compose --env-file $(ENV_FILE) logs -f

migrate:
	docker compose --env-file $(ENV_FILE) exec koinonia-api python manage.py migrate --noinput
	docker compose --env-file $(ENV_FILE) exec shepherds-toolkit-api python manage.py migrate --noinput

# Docker secrets nao sao atualizaveis in-place: remove (se existir) e recria.
# Rode de novo depois de trocar um valor no ENV_FILE.
secrets:
	set -a; . ./$(ENV_FILE); set +a; \
	create_secret() { \
		name=$$1; value=$$2; \
		docker secret rm $$name >/dev/null 2>&1 || true; \
		printf '%s\n' "$$value" | docker secret create $$name - >/dev/null && { \
			if [ -z "$$value" ]; then echo "  OK $$name (vazio)"; else echo "  OK $$name"; fi; \
		}; \
	}; \
	echo "Criando Docker secrets a partir de $(ENV_FILE)..."; \
	create_secret koinonia_secret_key "$$KOINONIA_SECRET_KEY"; \
	create_secret koinonia_db_password "$$KOINONIA_DB_PASSWORD"; \
	create_secret koinonia_fernet_key "$$KOINONIA_FERNET_KEY"; \
	create_secret koinonia_google_client_secret "$$KOINONIA_GOOGLE_CLIENT_SECRET"; \
	create_secret koinonia_client_secret "$$KOINONIA_CLIENT_SECRET"; \
	create_secret st_secret_key "$$ST_SECRET_KEY"; \
	create_secret st_db_password "$$ST_DB_PASSWORD"; \
	create_secret st_field_encryption_key "$$ST_FIELD_ENCRYPTION_KEY"; \
	create_secret st_auth0_client_secret "$$ST_AUTH0_CLIENT_SECRET"; \
	create_secret st_auth0_mgmt_client_secret "$$ST_AUTH0_MGMT_CLIENT_SECRET"; \
	create_secret st_google_client_secret "$$ST_GOOGLE_CLIENT_SECRET"; \
	create_secret st_openai_api_key "$$ST_OPENAI_API_KEY"; \
	create_secret st_stripe_secret_key "$$ST_STRIPE_SECRET_KEY"; \
	create_secret st_stripe_webhook_secret "$$ST_STRIPE_WEBHOOK_SECRET"

deploy: build
	set -a; . ./$(ENV_FILE); set +a; \
	docker stack deploy -c swarm-stack.yml koinonia --with-registry-auth

rm-stack:
	docker stack rm koinonia

ps:
	docker stack services koinonia

# ------------------------------------------------------------------
# Stack de teste (notebook usado como servidor de teste, via SSH)
# ------------------------------------------------------------------

secrets-test:
	set -a; . ./$(TEST_ENV_FILE); set +a; \
	create_secret() { \
		name=$$1; value=$$2; \
		docker secret rm $$name >/dev/null 2>&1 || true; \
		printf '%s\n' "$$value" | docker secret create $$name - >/dev/null && { \
			if [ -z "$$value" ]; then echo "  OK $$name (vazio)"; else echo "  OK $$name"; fi; \
		}; \
	}; \
	echo "Criando Docker secrets de teste a partir de $(TEST_ENV_FILE)..."; \
	create_secret test_koinonia_secret_key "$$KOINONIA_SECRET_KEY"; \
	create_secret test_koinonia_db_password "$$KOINONIA_DB_PASSWORD"; \
	create_secret test_koinonia_fernet_key "$$KOINONIA_FERNET_KEY"; \
	create_secret test_koinonia_google_client_secret "$$KOINONIA_GOOGLE_CLIENT_SECRET"; \
	create_secret test_koinonia_client_secret "$$KOINONIA_CLIENT_SECRET"; \
	create_secret test_st_secret_key "$$ST_SECRET_KEY"; \
	create_secret test_st_db_password "$$ST_DB_PASSWORD"; \
	create_secret test_st_field_encryption_key "$$ST_FIELD_ENCRYPTION_KEY"; \
	create_secret test_st_auth0_client_secret "$$ST_AUTH0_CLIENT_SECRET"; \
	create_secret test_st_auth0_mgmt_client_secret "$$ST_AUTH0_MGMT_CLIENT_SECRET"; \
	create_secret test_st_google_client_secret "$$ST_GOOGLE_CLIENT_SECRET"; \
	create_secret test_st_openai_api_key "$$ST_OPENAI_API_KEY"; \
	create_secret test_st_stripe_secret_key "$$ST_STRIPE_SECRET_KEY"; \
	create_secret test_st_stripe_webhook_secret "$$ST_STRIPE_WEBHOOK_SECRET"

deploy-test: build
	set -a; . ./$(TEST_ENV_FILE); set +a; \
	docker stack deploy -c swarm-stack.test.yml koinonia-test --with-registry-auth

rm-stack-test:
	docker stack rm koinonia-test

ps-test:
	docker stack services koinonia-test
