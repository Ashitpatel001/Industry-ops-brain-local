"""
core/model.py
Local LLM inference engine supporting Qwen OpenVINO INT4.
Provides real-time streaming token callbacks for responsive UI updates.
"""

import logging
import os
from pathlib import Path
from typing import Callable, Optional
from core.config import get_config

try:
    import openvino as ov
    from transformers import AutoTokenizer
    try:
        from optimum.intel.openvino import OVModelForCausalLM
    except ImportError:
        from optimum.intel import OVModelForCausalLM
except ImportError as e:
    ov = None
    AutoTokenizer = None
    OVModelForCausalLM = None

logger = logging.getLogger("LocalLLM")


class LocalLLM:
    """
    Qwen2.5-3B INT4 via OpenVINO (optimum.intel).
    """

    def __init__(self, model_dir: Optional[str] = None):
        cfg = get_config()
        self.model_dir = Path(model_dir if model_dir is not None else cfg.model_path)
        self.pipe = None
        self.backend = None
        self.tokenizer = None
        self._load()

    def _load(self):
        # Check if OpenVINO IR exists (look for .xml and .bin files)
        ov_xml = list(self.model_dir.glob("*.xml")) if self.model_dir.exists() else []
        ov_bin = list(self.model_dir.glob("*.bin")) if self.model_dir.exists() else []

        if ov_xml and ov_bin:
            self._load_openvino()
        else:
            raise FileNotFoundError(
                f"No Qwen OpenVINO INT4 model found in {self.model_dir}.\n"
                "Please run: python scripts/download_model.py"
            )

    def _load_openvino(self):
        """Primary: OpenVINO INT4 — Intel CPU/Arc GPU optimized via optimum.intel"""
        if ov is None or AutoTokenizer is None or OVModelForCausalLM is None:
            raise ImportError("Failed to import OpenVINO / optimum / transformers packages.")

        cfg = get_config()
        core = ov.Core()
        devices = core.get_available_devices()

        # Prefer Arc GPU (GPU.0 or GPU) -> fallback CPU
        if cfg.device != "AUTO" and cfg.device in devices:
            device = cfg.device
        else:
            device = "GPU" if "GPU" in devices else "CPU"

        logger.info(f"OpenVINO available devices: {devices}. Selected: {device}")

        ov_config = {}
        if device == "CPU":
            ov_config["NUM_STREAMS"] = "1"
            # Limit threads to physical cores or 8
            cpu_count = os.cpu_count() or 4
            try:
                if hasattr(os, "sched_getaffinity"):
                    cpu_count = len(os.sched_getaffinity(0))
            except Exception:
                pass
            ov_config["INFERENCE_NUM_THREADS"] = str(min(8, cpu_count))

        logger.info(f"Loading OVModelForCausalLM from {self.model_dir} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir), trust_remote_code=True)
        self.pipe = OVModelForCausalLM.from_pretrained(
            str(self.model_dir),
            compile=True,
            device=device,
            ov_config=ov_config if ov_config else None,
            trust_remote_code=True,
        )
        self.backend = f"OpenVINO/{device}"
        logger.info(f"Model loaded successfully: {self.backend}")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.1,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Generate text from prompt. Optional streaming callback for UI updates."""
        if not self.backend:
            raise RuntimeError("Model engine is not initialized.")

        return self._generate_openvino(prompt, max_new_tokens, temperature, stream_callback)

    def _generate_openvino(
        self,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        callback: Optional[Callable[[str], None]],
    ) -> str:
        import threading
        from transformers import TextIteratorStreamer

        inputs = self.tokenizer(prompt, return_tensors="pt")
        gen_kwargs = dict(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=max(temperature, 0.01),
            do_sample=temperature > 0,
        )

        if "pad_token_id" not in gen_kwargs and self.tokenizer.pad_token_id is not None:
            gen_kwargs["pad_token_id"] = self.tokenizer.pad_token_id
        elif "pad_token_id" not in gen_kwargs and self.tokenizer.eos_token_id is not None:
            gen_kwargs["pad_token_id"] = self.tokenizer.eos_token_id

        if callback and self.tokenizer:
            streamer = TextIteratorStreamer(
                self.tokenizer, skip_prompt=True, skip_special_tokens=True
            )
            gen_kwargs["streamer"] = streamer

            thread = threading.Thread(target=self.pipe.generate, kwargs=gen_kwargs)
            thread.start()

            full_text = []
            for new_text in streamer:
                callback(new_text)
                full_text.append(new_text)
            thread.join()
            return "".join(full_text)

        outputs = self.pipe.generate(**gen_kwargs)
        input_len = inputs["input_ids"].shape[1]
        result = self.tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
        return result

    @property
    def backend_label(self) -> str:
        return self.backend or "Not Loaded"
