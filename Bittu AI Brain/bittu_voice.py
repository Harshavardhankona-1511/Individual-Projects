import asyncio
import array
import os
import queue
import threading
import time
import sounddevice as sd
from dotenv import load_dotenv
from google import genai
from websockets.exceptions import ConnectionClosedError

try:
    import msvcrt
except ImportError:
    msvcrt = None

load_dotenv()

# Audio settings for Live API
FORMAT = "int16"
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHUNK_SIZE = 512
SILENCE_THRESHOLD = 60


def is_silent_pcm(data: bytes, threshold: int = SILENCE_THRESHOLD) -> bool:
    """Return True when the PCM chunk is effectively silent."""
    if not data:
        return True

    samples = array.array("h")
    samples.frombytes(data)
    if not samples:
        return True

    avg_abs = sum(abs(sample) for sample in samples) / len(samples)
    return avg_abs < threshold


def keyboard_reader(command_queue):
    """Read keyboard commands for push-to-talk and text fallback."""
    if msvcrt is None:
        print("⚠️ Keyboard controls are unavailable on this OS. Use the text fallback by typing a question in the terminal.")
        return

    print("Controls: Space = push-to-talk, T = type a question, Q = quit")
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key in (" ", "t", "T", "q", "Q"):
                command_queue.put(key)
        time.sleep(0.05)


async def listen_and_send(session, recording):
    """Captures microphone audio and streams it live to Gemini until a turn ends."""
    stream = sd.RawInputStream(
        samplerate=INPUT_RATE,
        channels=CHANNELS,
        dtype=FORMAT,
        blocksize=CHUNK_SIZE
    )

    silence_chunks = 0
    with stream:
        stream.start()
        print("🎤 Microphone active. Press Space to start talking, tap Space again to send, or type T for text mode.")
        while True:
            if not recording.is_set():
                await asyncio.sleep(0.05)
                continue

            data, _overflow = await asyncio.to_thread(stream.read, CHUNK_SIZE)
            if not data:
                continue

            if is_silent_pcm(data):
                silence_chunks += 1
                if silence_chunks >= 12:
                    await session.send_realtime_input(audio_stream_end=True)
                    recording.clear()
                    silence_chunks = 0
                    print("\n[Turn ended. You can ask another question.]\n")
                continue

            silence_chunks = 0
            audio_blob = {"data": bytes(data), "mime_type": f"audio/pcm;rate={INPUT_RATE}"}
            await session.send_realtime_input(audio=audio_blob)


async def command_handler(session, command_queue, recording):
    """Handle voice controls and text fallback commands."""
    while True:
        key = await asyncio.to_thread(command_queue.get)

        if key in ("q", "Q"):
            print("\nBittu session ended safely.")
            raise KeyboardInterrupt

        if key == " ":
            if recording.is_set():
                await session.send_realtime_input(audio_stream_end=True)
                recording.clear()
                print("\n[Voice sent. Awaiting the next prompt.]\n")
            else:
                recording.set()
                print("\n[Push-to-talk engaged. Speak now.]\n")
            continue

        if key in ("t", "T"):
            text = await asyncio.to_thread(input, "\nType your question and press Enter: ")
            text = text.strip()
            if text:
                print(f"\nYou: {text}")
                await session.send_realtime_input(text=text)


async def receive_and_play(session):
    """Receives audio response chunks from Gemini and plays them instantly."""
    stream = sd.RawOutputStream(
        samplerate=OUTPUT_RATE,
        channels=CHANNELS,
        dtype=FORMAT
    )

    with stream:
        stream.start()
        async for response in session.receive():
            server_content = response.server_content
            if server_content is not None:
                if server_content.interrupted:
                    print("\n[Interrupted]")
                    continue

                model_turn = server_content.model_turn
                if model_turn:
                    for part in model_turn.parts:
                        if part.inline_data:
                            await asyncio.to_thread(stream.write, part.inline_data.data)


async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in your .env file.")
        return

    client = genai.Client(api_key=api_key)
    model = "gemini-3.1-flash-live-preview"
    config = {"response_modalities": ["AUDIO"]}

    command_queue = queue.Queue()
    recording = asyncio.Event()

    thread = threading.Thread(target=keyboard_reader, args=(command_queue,), daemon=True)
    thread.start()

    while True:
        try:
            print(f"Connecting to {model}...")
            async with client.aio.live.connect(model=model, config=config) as session:
                print("✅ Connected! Bittu Live is ready.")
                try:
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(listen_and_send(session, recording))
                        tg.create_task(receive_and_play(session))
                        tg.create_task(command_handler(session, command_queue, recording))
                except* (ConnectionClosedError, TimeoutError, asyncio.TimeoutError):
                    print("\n[Connection lost. Reconnecting to Gemini Live...]")
        except (ConnectionClosedError, TimeoutError, asyncio.TimeoutError):
            print("\n[Live session timed out. Reconnecting in 2 seconds...]")

        await asyncio.sleep(2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBittu session ended safely.")
async def receive_and_play(session):
    """Receives audio response chunks from Gemini and plays them instantly."""
    stream = sd.RawOutputStream(
        samplerate=OUTPUT_RATE,
        channels=CHANNELS,
        dtype=FORMAT
    )
    
    with stream:
        stream.start()
        async for response in session.receive():
            server_content = response.server_content
            if server_content is not None:
                if server_content.interrupted:
                    print("\n[Interrupted]")
                    continue

                model_turn = server_content.model_turn
                if model_turn:
                    for part in model_turn.parts:
                        if part.inline_data:
                            await asyncio.to_thread(stream.write, part.inline_data.data)

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in your .env file.")
        return

    client = genai.Client(api_key=api_key)

    # Use the real-time live model
    model = "gemini-3.1-flash-live-preview"

    # Live API configuration using a native Python dictionary
    config = {
        "response_modalities": ["AUDIO"]
    }

    while True:
        try:
            print(f"Connecting to {model}...")
            async with client.aio.live.connect(model=model, config=config) as session:
                print("✅ Connected! Bittu Live is ready.")
                try:
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(listen_and_send(session))
                        tg.create_task(receive_and_play(session))
                except* (ConnectionClosedError, TimeoutError, asyncio.TimeoutError):
                    print("\n[Connection lost. Reconnecting to Gemini Live...]")
        except (ConnectionClosedError, TimeoutError, asyncio.TimeoutError):
            print("\n[Live session timed out. Reconnecting in 2 seconds...]")
        await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBittu session ended safely.")