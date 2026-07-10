from pathlib import Path
import shutil

import openvino as ov
import nncf
from nncf import CompressWeightsMode

INPUT_DIR = Path(r"D:\AI-local\models\qwen2.5-3b-fp16")
OUTPUT_DIR = Path(r"D:\AI-local\models\qwen2.5-3b-int4")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Loading FP16 OpenVINO model...")
core = ov.Core()

model = core.read_model(INPUT_DIR / "openvino_model.xml")

print("Compressing weights to INT4...")
compressed_model = nncf.compress_weights(
    model,
    mode=CompressWeightsMode.INT4_SYM,
    ratio=1.0,
    group_size=128,
)

print("Saving INT4 model...")
ov.save_model(
    compressed_model,
    OUTPUT_DIR / "openvino_model.xml",
)

print("Copying tokenizer/config files...")

files_to_copy = [
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "chat_template.jinja",
    "openvino_tokenizer.xml",
    "openvino_tokenizer.bin",
    "openvino_detokenizer.xml",
    "openvino_detokenizer.bin",
]

for file in files_to_copy:
    src = INPUT_DIR / file
    if src.exists():
        shutil.copy2(src, OUTPUT_DIR / file)

print("=" * 60)
print("SUCCESS!")
print(f"INT4 model saved to:\n{OUTPUT_DIR}")