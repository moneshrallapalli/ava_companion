# Ava Companion

Personal rebuild of the [Ava WhatsApp agent course](../GitHub/ava-whatsapp-agent-course/) by Monesh and Mouryan.

Ava is a multimodal LangGraph agent that chats in text, can reply with voice or images, remembers durable facts in Qdrant, and can be reached through Chainlit (local UI) or WhatsApp Cloud API.

## Status

**Application code for Days 1–27 is done.** What remains is configuration and live platform setup, not missing modules.

| Layer | Status |
|---|---|
| LangGraph brain (router, memory, summarize, conversation/image/audio) | Done |
| Speech (STT / TTS) + vision (ITT) + image gen (TTI) | Done |
| Production package layout (`core/`, `graph/`, `modules/`, `interfaces/`) | Done |
| Chainlit UI (text, image, audio + SQLite checkpointer) | Done |
| WhatsApp webhook (text + media in/out) | Done |
| Docker / Compose | Done |
| Live API keys in `.env` | **You** — refresh expired Groq key; fill the rest |
| WhatsApp Cloud API app + public webhook URL | **You** — Meta Developer setup |
| Cloud Run deploy | Optional — Docker is ready; GCP project/secrets still needed |
| Day 28 live WhatsApp demo + retro | Ops only, after keys + webhook |

Known non-blockers (also present in the answer key):

- `apply_activity` is written but never read
- `TextToImage.enhance_prompt` exists but is unused by `image_node`
- Chainlit uses a hard-coded `thread_id=1` (fine for solo demo)
- ElevenLabs / Together calls inside some `async` methods are still sync SDK calls

Week 1–3 scratch code remains under `src/ai_companion/lab/` as an archive. Prefer `graph/`, `modules/`, and `interfaces/`.

## Quick start

```bash
# 1. Python env
uv sync

# 2. Keys
cp .env.example .env
# Fill GROQ_*, ELEVENLABS_*, TOGETHER_*, QDRANT_*
# Add WHATSAPP_* only when testing the webhook

# 3. Local Chainlit UI
make chainlit
# → http://localhost:8000

# 4. Local WhatsApp webhook (needs Meta tokens + a tunnel like ngrok)
make webhook
# → http://localhost:8080/whatsapp_response

# 5. Full stack with local Qdrant
make ava-build && make ava-run
```

Key click-paths: [answer-key GETTING_STARTED.md](../GitHub/ava-whatsapp-agent-course/docs/GETTING_STARTED.md)  
Cloud Run (optional): [answer-key gcp_setup.md](../GitHub/ava-whatsapp-agent-course/docs/gcp_setup.md)

## Architecture

```
START
  → memory_extraction_node
  → router_node
  → context_injection_node
  → memory_injection_node
  → [conversation | image | audio]_node
  → [optional summarize_conversation_node]
  → END
```

Inbound audio/images are handled **outside** the graph (Chainlit / WhatsApp): STT or ITT turns them into text, then the graph runs. Outbound audio/image come from graph state (`audio_buffer`, `image_path`).

| Path | Role |
|---|---|
| `src/ai_companion/core/` | Prompts, exceptions, Ava weekday schedules |
| `src/ai_companion/graph/` | State, nodes, edges, chains/helpers |
| `src/ai_companion/modules/` | Speech, image, memory, schedule logic |
| `src/ai_companion/interfaces/chainlit/` | Local chat UI |
| `src/ai_companion/interfaces/whatsapp/` | Cloud API webhook |
| `src/ai_companion/lab/` | Weeks 1–3 learning archive |

## Environment

| Variable | Required for |
|---|---|
| `GROQ_API_KEY` | Chat, router, memory analysis, STT, ITT |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | TTS / audio replies |
| `TOGETHER_API_KEY` | Image generation |
| `QDRANT_URL`, `QDRANT_API_KEY` | Long-term memory |
| `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_TOKEN`, `WHATSAPP_VERIFY_TOKEN` | WhatsApp only |
| `SHORT_TERM_MEMORY_DB_PATH` | Optional; default `data/memory.db` |

## Learning history (Weeks 1–4)

Built day-by-day from a blank `uv` project, using the course repo only as an answer key after each attempt.

| Week | Focus | Result |
|---|---|---|
| 1 | Brain | Graph, routing, schedules, Qdrant memory |
| 2 | Senses | TTS, STT, TTI, ITT, summarization in `lab/` |
| 3 | Swap | Rebuild partner pieces; keep best async patterns |
| 4 | Integration | Promote to production layout + Chainlit + WhatsApp + Docker |

Original day-by-day assignment table (historical):

| Day | Piece |
|---|---|
| 1–7 | Setup → conversation → schedules → router → Qdrant → memory nodes |
| 8–14 | TTS → audio_node → TTI → image_node → STT → summarize → ITT |
| 15–21 | Week 3 swap rebuilds through ImageToText + retro |
| 22–27 | Promote modules → Chainlit → checkpointer → WhatsApp → Docker |
| 28 | Live WhatsApp demo (keys + Meta + public URL) |

## Makefile

| Target | What it does |
|---|---|
| `make chainlit` | Run Chainlit locally |
| `make webhook` | Run WhatsApp FastAPI webhook locally |
| `make ava-build` | Build Compose images |
| `make ava-run` | Start Qdrant + Chainlit + WhatsApp containers |
| `make ava-stop` | Stop containers |
| `make ava-delete` | Stop and wipe local memory/image volumes |
