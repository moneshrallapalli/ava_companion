.PHONY: ava-build ava-run ava-stop ava-delete chainlit webhook

ava-build:
	docker compose build

ava-run:
	docker compose up -d

ava-stop:
	docker compose down

ava-delete:
	docker compose down -v
	rm -rf short_term_memory long_term_memory generated_images

chainlit:
	mkdir -p data
	uv run chainlit run ai_companion/interfaces/chainlit/app.py -w

webhook:
	mkdir -p data
	uv run fastapi run ai_companion/interfaces/whatsapp/webhook_endpoint.py --port 8080
