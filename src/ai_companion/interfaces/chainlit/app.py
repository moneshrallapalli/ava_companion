from io import BytesIO

import chainlit as cl
from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from ai_companion.graph import graph_builder
from ai_companion.modules.image import ImageToText
from ai_companion.modules.speech import SpeechToText, TextToSpeech
from ai_companion.settings import settings

speech_to_text = SpeechToText()
text_to_speech = TextToSpeech()
image_to_text = ImageToText()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with a stable thread id for the checkpointer."""
    cl.user_session.set("thread_id", 1)


@cl.on_message
async def on_message(message: cl.Message):
    """Handle text messages and attached images (Days 23–24)."""
    msg = cl.Message(content="")
    content = message.content or ""

    if message.elements:
        for elem in message.elements:
            if isinstance(elem, cl.Image):
                with open(elem.path, "rb") as image_file:
                    image_bytes = image_file.read()
                try:
                    description = await image_to_text.analyze_image(
                        image_bytes,
                        "Please describe what you see in this image in the context of our conversation.",
                    )
                    content += f"\n[Image Analysis: {description}]"
                except Exception as exc:
                    cl.logger.warning(f"Failed to analyze image: {exc}")

    thread_id = cl.user_session.get("thread_id")

    async with cl.Step(type="run"):
        async with AsyncSqliteSaver.from_conn_string(
            settings.SHORT_TERM_MEMORY_DB_PATH
        ) as short_term_memory:
            graph = graph_builder.compile(checkpointer=short_term_memory)
            async for chunk in graph.astream(
                {"messages": [HumanMessage(content=content)]},
                {"configurable": {"thread_id": thread_id}},
                stream_mode="messages",
            ):
                if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(
                    chunk[0], AIMessageChunk
                ):
                    await msg.stream_token(chunk[0].content)

            output_state = await graph.aget_state(
                config={"configurable": {"thread_id": thread_id}}
            )

    workflow = output_state.values.get("workflow", "conversation")
    if workflow == "audio":
        response = output_state.values["messages"][-1].content
        audio_buffer = output_state.values["audio_buffer"]
        await cl.Message(
            content=response,
            elements=[
                cl.Audio(
                    name="Audio",
                    auto_play=True,
                    mime="audio/mpeg3",
                    content=audio_buffer,
                )
            ],
        ).send()
    elif workflow == "image":
        response = output_state.values["messages"][-1].content
        image = cl.Image(path=output_state.values["image_path"], display="inline")
        await cl.Message(content=response, elements=[image]).send()
    else:
        await msg.send()


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    """Collect inbound microphone audio chunks (Day 24)."""
    if chunk.isStart:
        buffer = BytesIO()
        buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)
    cl.user_session.get("audio_buffer").write(chunk.data)


@cl.on_audio_end
async def on_audio_end():
    """Transcribe voice input, run the graph, and reply with TTS audio (Day 24)."""
    audio_buffer = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)
    audio_data = audio_buffer.read()

    input_audio_el = cl.Audio(mime="audio/mpeg3", content=audio_data)
    await cl.Message(author="You", content="", elements=[input_audio_el]).send()

    transcription = await speech_to_text.transcribe(audio_data)
    thread_id = cl.user_session.get("thread_id")

    async with AsyncSqliteSaver.from_conn_string(
        settings.SHORT_TERM_MEMORY_DB_PATH
    ) as short_term_memory:
        graph = graph_builder.compile(checkpointer=short_term_memory)
        output_state = await graph.ainvoke(
            {"messages": [HumanMessage(content=transcription)]},
            {"configurable": {"thread_id": thread_id}},
        )

    reply_text = output_state["messages"][-1].content
    reply_audio = await text_to_speech.synthesize(reply_text)
    await cl.Message(
        content=reply_text,
        elements=[
            cl.Audio(
                name="Audio",
                auto_play=True,
                mime="audio/mpeg3",
                content=reply_audio,
            )
        ],
    ).send()
