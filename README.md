# Ava Companion

**A multimodal WhatsApp-ready AI companion** rebuilt from scratch by **Monesh Rallapalli** and **Mouryan Jayashankar**, inspired by the [Ava WhatsApp agent course](../GitHub/ava-whatsapp-agent-course/) (Ex Machina–style Turing-test chat agent).

Ava can:

- Chat naturally in text with a consistent character persona  
- Remember durable personal facts across sessions (long-term memory)  
- Know “what she’s doing right now” from a weekday activity schedule  
- Understand voice notes and images  
- Reply with voice notes or generated images when asked  
- Run locally via Chainlit, or as a WhatsApp Cloud API webhook  
- Deploy as containers (Docker Compose locally; Cloud Run–ready images)

This repo is the **finished product** of a 4-week pair rebuild: every piece was implemented, wired, and exercised against **live cloud APIs** (not mocks), then promoted from a scratch `lab/` package into a production module layout.

---

## Product overview

| Capability | How Ava does it |
|---|---|
| Conversation | Groq LLMs + Ava character card prompt |
| Routing | Structured classifier chooses `conversation` / `image` / `audio` |
| Short-term memory | LangGraph SQLite checkpointer (`thread_id` per chat / WhatsApp number) |
| Long-term memory | Qdrant vector store + MiniLM embeddings + memory extract/inject nodes |
| Activity context | Weekday schedule → injected into the character prompt |
| Speech in | Groq Whisper (Speech-to-Text) |
| Speech out | ElevenLabs (Text-to-Speech) |
| Vision in | Groq vision model (Image-to-Text) |
| Image out | Together AI FLUX (Text-to-Image) |
| Local UI | Chainlit (text, image upload, mic audio) |
| Messaging channel | WhatsApp Cloud API webhook (text + media in/out) |

Inbound audio and images are transcribed/described **at the interface layer**, then fed into the graph as normal text. Outbound audio/images come from graph state (`audio_buffer`, `image_path`) after the router picks a workflow.

---

## Architecture

### Agent graph (LangGraph)

```
START
  → memory_extraction_node      # write durable facts to Qdrant
  → router_node                 # conversation | image | audio
  → context_injection_node      # current Ava activity from schedule
  → memory_injection_node       # read relevant facts into prompt
  → [conversation_node | image_node | audio_node]
  → [summarize_conversation_node?]  # trim history when chats get long
  → END
```

The graph is compiled **without** a checkpointer for Studio/smoke tests, and **with** `AsyncSqliteSaver` at the Chainlit and WhatsApp boundaries so each conversation persists across requests.

### Package layout

```
src/ai_companion/
├── core/                 # prompts, exceptions, weekday schedules
├── graph/                # state, nodes, edges, chains, helpers
├── modules/
│   ├── speech/           # SpeechToText, TextToSpeech
│   ├── image/            # ImageToText, TextToImage
│   ├── memory/long_term/ # VectorStore, MemoryManager
│   └── schedules/        # ScheduleContextGenerator
├── interfaces/
│   ├── chainlit/         # local product UI
│   └── whatsapp/         # FastAPI Cloud API webhook
├── settings.py           # pydantic-settings (loaded at import)
└── lab/                  # Weeks 1–3 learning archive (kept for reference)
```

### Runtime topology

```
                 ┌─────────────────┐
                 │  Chainlit UI    │  localhost:8000
                 │  (dev / demo)   │
                 └────────┬────────┘
                          │
WhatsApp user ──Meta──►   │   ┌──────────────────────────┐
                          ├──►│  LangGraph Ava workflow  │
Webhook :8080 ◄───────────┘   │  + SQLite checkpointer   │
                              └────────────┬─────────────┘
                                           │
              ┌──────────────┬─────────────┼──────────────┬─────────────┐
              ▼              ▼             ▼              ▼             ▼
           Groq LLM      Groq Whisper   ElevenLabs    Together FLUX   Qdrant
           + vision        (STT)          (TTS)         (TTI)        Cloud
```

---

## Tech stack

| Layer | Choice |
|---|---|
| Language / packaging | Python 3.12, `uv`, `src/` layout |
| Agent orchestration | LangGraph + LangChain |
| Chat / routing / vision / STT | Groq (`ChatGroq`, Whisper, vision models) |
| TTS | ElevenLabs |
| Image generation | Together AI (FLUX) |
| Long-term memory | Qdrant Cloud + `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Short-term memory | `langgraph-checkpoint-sqlite` + `aiosqlite` |
| Local product UI | Chainlit 2.x |
| WhatsApp interface | FastAPI + WhatsApp Cloud API (`httpx`) |
| Config | `pydantic-settings` + `.env` |
| Containers | Docker, Docker Compose (Qdrant + Chainlit + WhatsApp) |
| Deploy target | Container images suitable for **Google Cloud Run** (and any OCI host) |

---

## Live / cloud validation

During the build we exercised the **real product path** against live services—not stubbed adapters:

| Surface | What was validated |
|---|---|
| **Groq** | Live chat, structured routing, memory analysis, Whisper STT, vision ITT |
| **ElevenLabs** | Live TTS synthesis into `audio_buffer` / Chainlit playback |
| **Together AI** | Live FLUX image generation to `generated_images/` |
| **Qdrant Cloud** | Live collection upsert/search for long-term memories (keepalive + memory demos) |
| **Chainlit** | End-to-end local product UI: text, image attach, audio round-trip + checkpointer |
| **WhatsApp path** | Full webhook implementation (verify + text/audio/image in/out) against Cloud API contracts |
| **Docker Compose** | Multi-service stack (Qdrant + Chainlit + WhatsApp containers) |
| **Cloud-ready packaging** | Production Dockerfiles (`Dockerfile`, `Dockerfile.chainlit`) for Cloud Run–style deploys |

Day-to-day API keys live in `.env` (never committed). Copy from `.env.example` to reconnect any environment.

---

## How to run

```bash
# Install
uv sync
cp .env.example .env   # fill live keys

# Local product UI
make chainlit
# → http://localhost:8000

# WhatsApp webhook (point Meta to this URL / tunnel)
make webhook
# → http://localhost:8080/whatsapp_response

# Full container stack
make ava-build && make ava-run
```

| Make target | Purpose |
|---|---|
| `make chainlit` | Local Chainlit product |
| `make webhook` | Local WhatsApp FastAPI webhook |
| `make ava-build` / `ava-run` / `ava-stop` | Compose lifecycle |
| `make ava-delete` | Tear down and wipe local memory/image volumes |

---

## Environment variables

| Variable | Used by |
|---|---|
| `GROQ_API_KEY` | LLM, router, memory analysis, STT, ITT |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | TTS |
| `TOGETHER_API_KEY` | Image generation |
| `QDRANT_URL`, `QDRANT_API_KEY` | Long-term memory |
| `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_TOKEN`, `WHATSAPP_VERIFY_TOKEN` | WhatsApp Cloud API |
| `SHORT_TERM_MEMORY_DB_PATH` | Checkpointer DB (default `data/memory.db`) |

Optional model overrides (`TEXT_MODEL_NAME`, `STT_MODEL_NAME`, `TTI_MODEL_NAME`, etc.) have sensible defaults in `settings.py`.

---

## How we built it

Pair rebuild over **4 weeks / 28 days**, using the course repo only as an **answer key after attempting each piece**:

| Week | Theme | Outcome |
|---|---|---|
| **1 — Brain** | Graph, conversation, schedules, router, Qdrant memory | Text Ava with activity + long-term memory |
| **2 — Senses** | TTS, STT, TTI, ITT, summarization | Full multimodal graph in `lab/` |
| **3 — Swap** | Each partner rebuilds the other’s pieces | Stronger ownership; kept async Groq clients and stricter validation where we beat the answer key |
| **4 — Integration** | Promote `lab/` → `graph/` + `modules/` + `interfaces/`, Chainlit, WhatsApp, Docker | Shippable product shape |

Learning notes for each builder remain in `monesh.md` / `mouryan.md`. The scratch package `src/ai_companion/lab/` is archived on purpose so the production imports stay clean.

---

## Design notes (intentional differences from the answer key)

- **Async Groq** for STT and ITT (`AsyncGroq` + `await`) instead of sync clients inside `async def`
- **Cached module factories** (`@lru_cache` getters) for speech/image clients
- **No bearer-token `print()`** in the WhatsApp sender (answer-key wart removed)
- **Chainlit 2.11** audio API (`InputAudioChunk`, updated `on_audio_end`)
- Same intentional leftovers as the course (harmless): unused `apply_activity`, unused `enhance_prompt` on the graph path, solo-demo `thread_id=1` in Chainlit

---

## Authors

- **Monesh Rallapalli**
- **Mouryan Jayashankar**

Course / answer-key inspiration: [ava-whatsapp-agent-course](../GitHub/ava-whatsapp-agent-course/).
