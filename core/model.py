"""
core/model.py
Local LLM inference engine supporting Qwen OpenVINO INT4.
Provides real-time streaming token callbacks for responsive UI updates.
"""

import logging
import os
import re
import time
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
        cfg = get_config()
        if cfg.mock_llm:
            self.backend = "MockLLM"
            logger.info("Initializing in Mock LLM Mode (No download, local execution)")
            return

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

        if self.backend == "MockLLM":
            return self._generate_mock(prompt, stream_callback)

        return self._generate_openvino(prompt, max_new_tokens, temperature, stream_callback)

    def _generate_mock(self, prompt: str, stream_callback: Optional[Callable[[str], None]] = None) -> str:
        # Extract user question
        user_question = ""
        q_match = re.search(r"USER QUESTION:\s*(.*?)(?=\n|$)", prompt, re.IGNORECASE)
        if q_match:
            user_question = q_match.group(1).strip()

        # Extract sources from context
        sources = re.findall(r"Source \[(\d+)\] \((.*?)\):", prompt)

        q_lower = user_question.lower()

        # Generate intelligent mock response based on prompt keyword analysis
        if any(w in q_lower for w in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "welcome"]):
            answer = "Hello! I am Ops Brain Local, your on-device Industrial Safety, Maintenance, and Reliability Co-Pilot. I can assist you with P&ID diagnostics, maintenance work orders, OISD/Factory Act compliance, and 5-Why RCA analysis. How can I help you today?"
            citations = "None"
            confidence = "HIGH"
            actions = []
        elif any(w in q_lower for w in ["compliance", "audit", "regulation", "act", "rule", "oisd", "factory", "standards"]):
            if sources:
                doc_names = ", ".join([f"[{s[0]}] {s[1]}" for s in sources])
                answer = f"According to the safety regulations and compliance documents ({doc_names}), all industrial operations must strictly adhere to the standard safety guidelines. Specifically, the maintenance logs and equipment inspections must be documented at the scheduled intervals to ensure complete regulatory compliance. Section 4 of the Factory Act requires safety certification for all pressure vessels and heavy machinery before commissioning."
                citations = ", ".join([f"[{s[0]}]" for s in sources])
                confidence = "HIGH"
            else:
                answer = "I couldn't find any specific compliance documents in the local database. Generally, under the Factories Act and OISD guidelines, industrial plants must maintain regular maintenance logs, conduct safety audits of high-pressure systems, and display emergency response plans. Please upload your plant's specific safety manuals for a detailed compliance check."
                citations = "None"
                confidence = "MEDIUM"
            actions = [
                "Review safety compliance logs for the current quarter.",
                "Ensure all safety relief valves (SRV) are tested and tagged.",
                "Verify that emergency shut-down (ESD) systems are functional.",
                "Conduct a walkthrough safety audit of the processing unit."
            ]
        elif any(w in q_lower for w in ["pump", "bearing", "motor", "vibration", "temperature", "rca", "failure", "maintenance", "leak", "valve"]):
            if sources:
                doc_names = ", ".join([f"[{s[0]}] {s[1]}" for s in sources])
                answer = f"The analysis of the retrieved documents ({doc_names}) indicates a potential equipment fault or maintenance requirement. Historically, issues with this class of machinery often stem from lubrication breakdown, misalignment, or bearing wear, leading to elevated vibration and temperature levels. Refer to the maintenance manual ({doc_names}) for the recommended troubleshooting steps."
                citations = ", ".join([f"[{s[0]}]" for s in sources])
                confidence = "HIGH"
            else:
                answer = "The query regarding equipment performance indicates a typical mechanical or electrical issue. Based on standard industrial practices, equipment issues like excessive vibration or temperature are commonly caused by misalignment, bearing degradation, or lack of proper lubrication. I recommend initiating a Root Cause Analysis (RCA) starting with physical checks."
                citations = "None"
                confidence = "MEDIUM"
            actions = [
                "Perform a physical check on lube oil levels and quality.",
                "Measure vibration levels using a portable analyzer.",
                "Check shaft alignment and coupling condition.",
                "Review the past 5-Why analysis reports for this equipment group."
            ]
        else:
            if sources:
                doc_names = ", ".join([f"[{s[0]}] {s[1]}" for s in sources])
                answer = f"Based on the retrieved context ({doc_names}), I have extracted the relevant operational information. The documents suggest that the procedures should follow the standard operating parameters as defined in the manuals. Please review the specific sections in [1] for detailed step-by-step instructions."
                citations = ", ".join([f"[{s[0]}]" for s in sources])
                confidence = "HIGH"
            else:
                answer = f"I am ready to assist with your query: '{user_question}'. However, no direct matching documents were found in the local vector database. You can upload relevant PDFs or Excel sheets (e.g., equipment manuals, safety guidelines) via the file upload section to get specific answers."
                citations = "None"
                confidence = "LOW"
            actions = [
                "Upload relevant PDFs or text manuals in the sidebar.",
                "Verify the tags and IDs of the equipment being queried.",
                "Check the status of the local ingestion pipeline."
            ]

        # Format strictly according to core/pipeline.py parser guidelines
        full_output = f"ANSWER: {answer}\nCITATIONS: {citations}\nCONFIDENCE: {confidence}\nRECOMMENDED ACTIONS:\n"
        if not actions:
            full_output += "None\n"
        else:
            for action in actions:
                full_output += f"- {action}\n"

        if stream_callback:
            # Simulate a realistic streaming typing effect
            words = full_output.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + " "
                stream_callback(chunk)
                time.sleep(0.05)
        
        return full_output

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
