# Ava Build Plan - Monesh & Mouryan

You are both complete beginners to this stuff (LLMs, agents, LangGraph, vector DBs, voice/vision
APIs). This plan assumes that. Every new concept gets a plain-English explanation before any code.

## Why this exists

The repo is already fully built. The goal is NOT to read the finished code and nod along —
it's to rebuild each piece yourselves, in small daily increments, using the real implementation
only as an answer key to check against *after* you've attempted it. Every day ends with wiring
your new piece into a shared LangGraph graph, so integration is a daily habit, not a week-4 panic.

## The rules

1. **One small piece per day.** Not a whole module, not a whole lesson — one node or one helper.
2. **Build it standalone first, then wire it into the graph the same day.** ~15-20 min integration
   step at the end of each day, done together.
3. **Daily standup:** whoever built yesterday's piece explains it in depth to the other person —
   what state it reads, what it returns, why it's shaped that way, in plain English, no jargon
   without explaining the jargon first. The other person should be able to ask "why" and get a
   real answer, not "that's just how the repo does it."
4. **Check against the answer key after you attempt it, not before.** Each day lists the real file
   path — don't open it until you've written your own version and tested it.
5. **Alternate who builds the next piece**, following the real dependency order below.
6. **Build in your own project; never edit the answer-key repo.** All your code lives in this
   `ava_companion/` project (see "Project setup" below). During Weeks 1-3, build everything in a
   scratch package `src/ai_companion/lab/` — freely breakable, no fear of wrecking anything. In
   Week 4 you promote your best `lab/` code into the real module shape (`src/ai_companion/graph/`,
   `src/ai_companion/modules/`, `src/ai_companion/interfaces/`). The cloned repo at
   `../GitHub/ava-whatsapp-agent-course/` is the **answer key** — read it after you attempt each
   piece, never edit it.

## Project setup (this is YOUR project, built from scratch — read before Day 1)

Nothing here is pre-built. Unlike the answer-key repo, you create the project shell yourself:

- A `uv` project named `ai-companion`, pinned to Python **3.12** (match the repo), in a `src/`
  layout so your code is importable as `ai_companion.*`.
- Dependencies added **incrementally with `uv add`**, the day you first need each one — not all at
  once. Week 1 only needs `langgraph`, `langchain`, `langchain-groq`, and `pydantic-settings`.
- Your own `settings.py` (a `pydantic_settings.BaseSettings` class, built on Day 3 when first
  needed) and your own `.env`. The repo's `.env.example` lists every key name to copy into your
  `.env`.
- Qdrant (from Day 6) and the full app (Week 4) you run yourself via Docker. The repo's
  `docker-compose.yml`, `Makefile`, and `Dockerfile` are references to read — you'll write your own.

### Keys: fill them on Day 1, even the ones Week 1 doesn't use

Create your `.env` with all the service keys (Groq, ElevenLabs API key + voice ID, Together, Qdrant
URL/key) filled in. Leave only the three `WHATSAPP_*` ones empty until Week 4. The click-path for
each key is in the repo's
[GETTING_STARTED.md](../GitHub/ava-whatsapp-agent-course/docs/GETTING_STARTED.md).

Why fill all of them up front, even though Week 1 only uses Groq? Because of two behaviors you'll
deliberately build into your own code, mirroring the answer key:
- Your `settings.py` will build its `Settings` object **at import time** (a `settings = Settings()`
  line at the bottom). Every field is required, so even an empty string must be present in `.env`
  for `import` to succeed — a missing key *name* raises immediately.
- Each media module (`SpeechToText`, `TextToSpeech`, ...) will run a `_validate_env_vars()` check
  that treats an **empty string as missing** and raises at construction time. So an empty Groq or
  ElevenLabs key would crash the full app at startup, while empty Together/Qdrant values fail the
  moment you hit image generation or long-term memory. Filling everything on Day 1 means nothing
  surprises you later.

## Concept glossary (read this before Day 1)

- **LLM (Large Language Model):** a model that takes text in, produces text out, called over an
  API (here, Groq). You don't train it — you just send it a prompt and get a response.
- **Agent:** a program where an LLM's output decides what happens next (which tool to call, which
  path to take), instead of the program following one fixed path every time.
- **LangGraph:** a library for building agents as a **graph** — a flowchart where each step is a
  **node** (a function) and the arrows between them are **edges**. The graph carries a shared
  **state** (a dict-like object) that every node can read from and write to.
- **State / Node / Edge:** state = the data passed along the graph (e.g. the conversation
  messages). Node = a function that takes the state and returns updates to it. Edge = "after this
  node, go to that node." A **conditional edge** picks the next node based on what's in the state
  (like an if/else for the graph).
- **Prompt / System prompt:** the text instructions you give an LLM. A "system prompt" sets the
  persona/rules ("You are Ava, a witty companion...") separately from the actual user message.
- **Structured output:** asking the LLM to respond in a fixed shape (e.g. a Python class with
  specific fields) instead of free text, so your code can reliably use the result.
- **Embedding:** a way of turning text into a list of numbers (a vector) such that similar
  meanings end up as similar vectors. This is how "search by meaning" works instead of exact
  keyword matching.
- **Vector database (Qdrant here):** a database built to store embeddings and quickly find the
  ones most similar to a query embedding — this is what gives Ava long-term memory.
- **Memory extraction vs. injection (two separate steps):** *extraction* looks at the user's
  newest message, decides if it contains a fact worth keeping, and **writes** it to the vector DB.
  *Injection* takes the current conversation, **reads** the most relevant stored facts back out,
  and pastes them into Ava's prompt. In the real graph these are two different nodes sitting at
  two different positions — extraction runs first (a write), injection runs later (a read). Keep
  them straight; it's the single most common point of confusion in this project.
- **STT / TTS:** Speech-to-Text (audio -> text, via Whisper) and Text-to-Speech (text -> audio, via
  ElevenLabs).
- **Diffusion model / TTI:** Text-to-Image generation (via a FLUX model on Together AI) — text
  prompt in, generated image out.
- **Webhook:** a URL that an external service (WhatsApp) calls automatically when something
  happens (a user sends a message), instead of you having to poll/ask "any new messages?"
  repeatedly.
- **Checkpointer / short-term memory:** LangGraph's mechanism for saving the conversation state to
  disk between messages, keyed by a `thread_id`, so the agent "remembers" the current conversation
  across separate HTTP requests.

## The real graph (the map you're rebuilding)

```
START
  -> memory_extraction_node
  -> router_node
  -> context_injection_node
  -> memory_injection_node
  -> [conditional: select_workflow]
       -> conversation_node
       -> image_node
       -> audio_node
  -> [conditional: should_summarize_conversation]
       -> summarize_conversation_node -> END
       -> END
```

Source: [graph.py](../GitHub/ava-whatsapp-agent-course/src/ai_companion/graph/graph.py), [nodes.py](../GitHub/ava-whatsapp-agent-course/src/ai_companion/graph/nodes.py),
[edges.py](../GitHub/ava-whatsapp-agent-course/src/ai_companion/graph/edges.py), [state.py](../GitHub/ava-whatsapp-agent-course/src/ai_companion/graph/state.py).

Read that order carefully: **memory_extraction runs first** (before the router), and
**memory_injection runs fourth** (after context). They are not the same node and they are not next
to each other. The router sits *between* the two memory steps.

## Imperfections in the real code (you'll find these — don't treat the repo as gospel)

Part of learning is noticing where production code is messy or wrong. The answer key has real warts.
When you hit these, the goal is to *recognize* them, not copy them blindly:

- **`apply_activity` is dead state.** `context_injection_node` computes `apply_activity` and stores
  it in state, but **nothing ever reads it** — the character prompt only receives `current_activity`
  and `memory_context`. It looks like it was meant to drive a "you just started a new activity" vs
  "still doing the same thing" distinction that never got wired up. Treat it as vestigial.
- **`enhance_prompt` is unused in the graph path.** `TextToImage.enhance_prompt` exists and works,
  but `image_node` calls `create_scenario` + `generate_image` directly and never calls it. Another
  orphaned method.
- **`RouterResponse` uses a plain `str`, not a `Literal`.** The repo relies on the *prompt* to keep
  the model outputting only `conversation`/`image`/`audio`. Using `Literal[...]` would enforce that
  in code at parse time — arguably better. You'll build it the better way and note the difference.
- **The WhatsApp handler prints the bearer token.** `send_response` does `print(headers)`, and
  `headers` contains `Authorization: Bearer <WHATSAPP_TOKEN>`. That leaks a live credential into
  logs. You'll find and fix this in Week 4.
- **Chainlit uses a hard-coded `thread_id`.** `on_chat_start` sets `thread_id` to `1`, which is fine
  for a solo local demo but does **not** separate multiple users/sessions. A production version should
  use the Chainlit session/user id or another per-conversation key.
- **Some `async` media methods call synchronous SDK methods internally.** For example, several
  `async def` wrappers call `.convert(...)`, `.invoke(...)`, or Groq/Together client methods without
  an `await`. That can block the event loop. For this small course app it's survivable, but don't
  learn the wrong lesson: `async def` alone does not make blocking work non-blocking.

## The 4-week roadmap

**Week 1 — The Brain.** Skeleton graph, real chat, "what is Ava doing right now" context, routing
between response types, persistent memory via Qdrant. End state: a real chatting Ava with
activity-awareness, routing, and memory — text only.

**Week 2 — The Senses.** Text-to-speech, speech-to-text, text-to-image (generation), image-to-text
(vision), wired into `audio_node` and `image_node`, plus conversation summarization so long chats
don't blow past the model's context window. End state: the full graph, matching the real one
exactly, in your `lab/` module.

**Week 3 — Swap.** Each of you rebuilds, from scratch and in your own words, the pieces the *other*
person built in Weeks 1-2. You now have three versions of everything to compare: your partner's,
your own, and the repo's. This is where the explaining-out-loud habit gets tested for real.

**Week 4 — Integration, together.** `interfaces/chainlit` (the local chat UI), `interfaces/whatsapp`
(the real webhook), Docker + Cloud Run deploy. This part isn't split — it touches the whole system,
so you pair on all of it.

## Day-by-day assignment

| Day | Week | Builder | Piece |
|---|---|---|---|
| 1 | 1 | Both | Setup + concepts + read the map |
| 2 | 1 | Both | Skeleton graph (echo node) |
| 3 | 1 | Monesh | `conversation_node` + chat model |
| 4 | 1 | Mouryan | schedules + `context_injection_node` |
| 5 | 1 | Monesh | `router_node` + conditional routing |
| 6 | 1 | Mouryan | Qdrant vector store |
| 7 | 1 | Monesh + joint | `memory_manager` + **both** memory nodes (extraction + injection), full graph assembly in real order, demo |
| 8 | 2 | Mouryan | `TextToSpeech` (ElevenLabs) |
| 9 | 2 | Monesh | `audio_node` |
| 10 | 2 | Mouryan | `TextToImage` (Together AI / FLUX) |
| 11 | 2 | Monesh | `image_node` |
| 12 | 2 | Mouryan | `SpeechToText` (Whisper) |
| 13 | 2 | Monesh | `summarize_conversation_node` |
| 14 | 2 | Both | `ImageToText` (vision) + full graph integration demo |
| 15 | 3 | Swap | Mouryan rebuilds `conversation_node` / Monesh rebuilds `context_injection_node` |
| 16 | 3 | Swap | Mouryan rebuilds `router_node` / Monesh rebuilds vector store |
| 17 | 3 | Swap | Mouryan rebuilds `memory_manager` + both memory nodes / Monesh rebuilds `TextToSpeech` |
| 18 | 3 | Swap | Mouryan rebuilds `audio_node` / Monesh continues `TextToSpeech` integration |
| 19 | 3 | Swap | Mouryan rebuilds `image_node` / Monesh rebuilds `TextToImage` |
| 20 | 3 | Swap | Mouryan rebuilds `summarize_conversation_node` / Monesh rebuilds `SpeechToText` |
| 21 | 3 | Both | Monesh rebuilds `ImageToText` + full review/retro of all 3 versions |
| 22 | 4 | Both | Promote `lab/` learnings into the real graph shape, diff against repo |
| 23 | 4 | Both | Chainlit text + image interface |
| 24 | 4 | Both | Chainlit audio interface + short-term memory checkpointer |
| 25 | 4 | Both | WhatsApp webhook (verification + text messages) |
| 26 | 4 | Both | WhatsApp media (audio/image in and out) |
| 27 | 4 | Both | Docker + Cloud Run deploy |
| 28 | 4 | Both | End-to-end demo on real WhatsApp + retro |

Swap who goes "first" on the new thing each week if you want — the table above is a default, not a
rule.
