import os

os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
import io
import torch
import numpy as np
import soundfile as sf
import librosa
from threading import Lock

STT_MODEL_ID = "openai/whisper-large-v3-turbo"
TTS_MODEL_DIR = "models/voice"

PIPER_MODELS = {
    "en": {
        "onnx": "en_US-lessac-medium.onnx",
        "json": "en_US-lessac-medium.onnx.json",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    },
    "ar": {
        "onnx": "ar_JO-kareem-medium.onnx",
        "json": "ar_JO-kareem-medium.onnx.json",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx.json",
    },
}

VOICE_LLM_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

_stt_processor = None
_stt_model = None
_tts_pipelines = {}
_voice_llm = None

_voice_lock = Lock()


def _download_file(url, dest):
    import os
    import urllib.request
    import logging

    logger = logging.getLogger("iris")
    logger.info(f"[Voice] Downloading {os.path.basename(dest)}...")

    downloaded = False
    if "huggingface.co" in url and "/resolve/" in url:
        try:
            from huggingface_hub import hf_hub_download

            parts = url.split("huggingface.co/")[-1].split("/resolve/")
            repo_id = parts[0]
            subparts = parts[1].split("/")
            remote_name = "/".join(subparts[1:])
            logger.info("  [Voice] Using accelerated Xet high-performance transfer...")

            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            dl_path = hf_hub_download(
                repo_id=repo_id,
                filename=remote_name,
                local_dir=os.path.dirname(dest) or ".",
                local_dir_use_symlinks=False,
            )
            if os.path.abspath(dl_path) != os.path.abspath(dest):
                if os.path.exists(dest):
                    os.remove(dest)
                os.rename(dl_path, dest)
            downloaded = True
        except Exception as e:
            logger.info(
                f"  [Voice] HF transfer failed ({e}), falling back to standard download..."
            )

    if not downloaded:
        urllib.request.urlretrieve(url, dest)

    logger.info(f"[Voice] Downloaded {os.path.basename(dest)}")


def load_stt_model():
    global _stt_processor, _stt_model
    with _voice_lock:
        if _stt_model is not None:
            return _stt_processor, _stt_model

        import logging

        logging.getLogger("iris").info(f"[Voice] Loading STT model: {STT_MODEL_ID}")

        logging.getLogger("transformers").setLevel(logging.ERROR)

        from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

        device = (
            "cuda"
            if torch.cuda.is_available()
            else ("mps" if torch.backends.mps.is_available() else "cpu")
        )
        _stt_processor = AutoProcessor.from_pretrained(STT_MODEL_ID)
        _stt_model = AutoModelForSpeechSeq2Seq.from_pretrained(STT_MODEL_ID).to(device)

        return _stt_processor, _stt_model


def load_tts_model(lang="en"):
    global _tts_pipelines
    with _voice_lock:
        if lang in _tts_pipelines:
            return _tts_pipelines[lang]

        import logging

        logging.getLogger("iris").info(f"[Voice] Loading Piper TTS model ({lang})")

        os.makedirs(TTS_MODEL_DIR, exist_ok=True)
        conf = PIPER_MODELS[lang]

        onnx_path = os.path.join(TTS_MODEL_DIR, conf["onnx"])
        json_path = os.path.join(TTS_MODEL_DIR, conf["json"])

        if not os.path.exists(onnx_path):
            _download_file(conf["url"], onnx_path)
        if not os.path.exists(json_path):
            _download_file(conf["json_url"], json_path)

        from piper import PiperVoice

        use_cuda = torch.cuda.is_available()
        _tts_pipelines[lang] = PiperVoice.load(
            onnx_path, config_path=json_path, use_cuda=use_cuda
        )

        return _tts_pipelines[lang]


def load_voice_llm():
    global _voice_llm
    with _voice_lock:
        if _voice_llm is not None:
            return _voice_llm

        import logging

        logging.getLogger("iris").info(
            "[Voice] Loading ultra-fast Conversational LLM (Qwen2.5-1.5B)"
        )

        _root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        llm_path = os.path.join(_root_dir, "models", "iris_009.gguf")

        if not os.path.exists(llm_path):
            _download_file(VOICE_LLM_URL, llm_path)

        from llama_cpp import Llama

        _voice_llm = Llama(
            model_path=llm_path, n_ctx=2048, n_gpu_layers=-1, n_threads=4, verbose=False
        )
        return _voice_llm


def transcribe_audio(audio_data: bytes, original_filename: str) -> str:

    processor, model = load_stt_model()
    device = (
        "cuda"
        if torch.cuda.is_available()
        else ("mps" if torch.backends.mps.is_available() else "cpu")
    )

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name

    try:
        audio_array, sr = librosa.load(tmp_path, sr=16000)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    inputs = processor(audio_array, return_tensors="pt", sampling_rate=16000)
    inputs = {
        k: (
            v.to(device=device, dtype=model.dtype)
            if torch.is_floating_point(v)
            else v.to(device)
        )
        for k, v in inputs.items()
    }

    with torch.no_grad():
        output = model.generate(**inputs)

    text = processor.decode(output[0], skip_special_tokens=True)
    return text.strip()


def synthesize_speech(text: str) -> str:

    import re
    import logging
    import asyncio
    import base64
    from edge_tts import Communicate

    logger = logging.getLogger("iris")

    if not text.strip():
        return None

    try:
        logger.info("[Voice] Generating Edge Neural TTS response...")

        is_ar = bool(re.search(r"[\u0600-\u06FF]", text))
        voice = "ar-EG-SalmaNeural" if is_ar else "en-US-AriaNeural"

        async def get_audio_bytes(text, voice):

            communicate = Communicate(text, voice, rate="+12%", pitch="+4Hz")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(get_audio_bytes(text.strip(), voice))

        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

        return f"data:audio/mp3;base64,{b64_audio}"

    except Exception as e:
        logger.error(f"[Voice] TTS failed: {e}")
        return None
