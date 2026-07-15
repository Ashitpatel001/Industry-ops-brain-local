#!/usr/bin/env python3
"""
scripts/create_sample_pdf.py
============================
Generates a realistic industrial technical manual PDF (SOP_P204_Crude_Pump_Maintenance_Manual.pdf)
and markdown equivalent inside data/uploads/ for testing the Ingestion & Graph Extraction Studio.
"""

import os
from pathlib import Path

def generate_sample_documents():
    out_dir = Path("data/uploads")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create clean Markdown / TXT version
    md_path = out_dir / "SOP_P204_Crude_Pump_Maintenance_Manual.md"
    md_content = """# OPERATING AND MAINTENANCE MANUAL: CRUDE CHARGE PUMP P-204
**Document ID:** SOP-PMP-204-REV4 | **Process Unit:** Unit-5 (CDU) | **Criticality:** HIGH

---

## 1.0 EQUIPMENT OVERVIEW & TECHNICAL SPECIFICATIONS
The Crude Charge Pump (Tag: `P-204`) is a heavy-duty, horizontal, multi-stage centrifugal pump designed for API 610 compliance. It feeds raw crude oil into the primary distillation column under high pressure and temperature.
- **Operating Temperature:** 240 °C to 285 °C
- **Discharge Pressure:** 42.5 Bar
- **Rated Flow Rate:** 850 m³/hr
- **MTBF Target:** > 365 Days | **Current MTBF:** 67 Days *(ACTION REQUIRED)*
- **Mechanical Seal Type:** Dual Cartridge API 682 Plan 53B with external barrier fluid flushing.
- **Downstream Dependency:** Pre-Heat Exchanger Bank (`HX-301`) and High Pressure Separator Vessel (`V-112`).

---

## 2.0 RECURRING FAILURE MODE: MECHANICAL SEAL & FLUSH LINE RESTRICTION
Historical telemetry and root cause analyses (`RCA-F71895`) indicate persistent bearing and seal breakdowns on `P-204`.

### 2.1 Primary Causes of Failure (`FM-001`):
1. Accumulation of particulate coking debris inside the API 682 Plan 11 flush orifice.
2. Loss of barrier fluid pressure in Plan 53B accumulator bladder.
3. Thermal face distortion resulting from dry running during feedstock changeovers.

### 2.2 Mandatory Preventive Maintenance Actions (`SOP-PMP-001`):
- **Step 1:** Weekly inspection and cleaning of inline duplex strainers on the seal flush piping.
- **Step 2:** Continuous verification of barrier fluid nitrogen accumulator pressure (Must exceed chamber pressure by at least 2.0 Bar).
- **Step 3:** Immediate vibration spectral check if RMS velocity exceeds 4.5 mm/s.

---

## 3.0 STATUTORY COMPLIANCE & CONFINED SPACE SAFETY (`OISD-GDN-192` / `OISD-116`)
Any maintenance turnaround involving internal seal cartridge replacement or casing drainage falls under mandatory statutory safety procedures.

### 3.1 Confined Space Entry (CSE) Requirements (`OISD-GDN-192` Section 4.2):
- Prior to opening pump casing or associated drain lines, positive isolation (Double Block and Bleed with Spectacle Blind) MUST be executed.
- Atmospheric testing using a calibrated 4-gas detector must confirm:
  - **Oxygen (O2):** Level between 19.5% and 23.5%.
  - **Lower Explosive Limit (LEL):** Exactly 0.0%.
  - **Hydrogen Sulfide (H2S):** < 5 PPM.

### 3.2 Fire & Hazardous Material Protocol (`Factory Act 1948` Sec 36):
- Standby fire watch equipped with dry chemical extinguisher required for any hot work within 15 meters of `P-204`.
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[SUCCESS] Created industrial sample document -> {md_path}")

    # 2. Create minimal valid PDF version with exact text stream
    pdf_path = out_dir / "SOP_P204_Crude_Pump_Maintenance_Manual.pdf"
    text_pages = [
        "OPERATING AND MAINTENANCE MANUAL: CRUDE CHARGE PUMP P-204\nDocument ID: SOP-PMP-204-REV4 | Process Unit: Unit-5 (CDU) | Criticality: HIGH\n\n1.0 EQUIPMENT OVERVIEW & TECHNICAL SPECIFICATIONS\nThe Crude Charge Pump (Tag: P-204) is a heavy-duty centrifugal pump feeding raw crude oil under high pressure.\n- Operating Temperature: 240 C to 285 C | Discharge Pressure: 42.5 Bar\n- MTBF Target: > 365 Days | Current MTBF: 67 Days (ACTION REQUIRED)\n- Mechanical Seal Type: Dual Cartridge API 682 Plan 53B.\n- Downstream Dependency: Pre-Heat Exchanger Bank (HX-301).",
        
        "2.0 RECURRING FAILURE MODE: MECHANICAL SEAL & FLUSH LINE RESTRICTION\nHistorical analyses (RCA-F71895) indicate persistent bearing and seal breakdowns on P-204.\n2.1 Primary Causes of Failure (FM-001):\n- Accumulation of particulate coking debris inside the API 682 Plan 11 flush orifice.\n- Loss of barrier fluid pressure in Plan 53B accumulator bladder.\n- Thermal face distortion resulting from dry running during feedstock changeovers.\n\n2.2 Mandatory Preventive Actions (SOP-PMP-001):\n1. Weekly inspection of inline duplex strainers on the seal flush piping.\n2. Verify barrier fluid nitrogen accumulator pressure exceeds chamber by >= 2.0 Bar.\n3. Immediate vibration spectral check if RMS velocity exceeds 4.5 mm/s.",
        
        "3.0 STATUTORY COMPLIANCE & CONFINED SPACE SAFETY (OISD-GDN-192 / OISD-116)\nAny turnaround involving seal cartridge replacement falls under mandatory statutory safety procedures.\n3.1 Confined Space Entry (CSE) Requirements (OISD-GDN-192 Section 4.2):\n- Positive isolation (Double Block and Bleed with Spectacle Blind) MUST be executed before opening.\n- Atmospheric testing must confirm: Oxygen (19.5%-23.5%), LEL (0.0%), H2S (< 5 PPM).\n3.2 Fire Protocol (Factory Act 1948 Sec 36):\n- Standby fire watch equipped with dry chemical extinguisher required for any hot work within 15m of P-204."
    ]

    objects = []
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    
    pages_str = " ".join([f"{3 + i*2} 0 R" for i in range(len(text_pages))])
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{pages_str}] /Count {len(text_pages)} >>\nendobj\n")
    
    font_obj_idx = 3 + len(text_pages)*2
    for i, content in enumerate(text_pages):
        page_obj_idx = 3 + i*2
        content_obj_idx = page_obj_idx + 1
        
        lines = content.split("\n")
        stream_lines = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
        for line in lines:
            clean_l = line.replace("(", "[").replace(")", "]").replace("\\", "/")
            stream_lines.append(f"({clean_l}) Tj T*")
        stream_lines.append("ET")
        stream_content = "\n".join(stream_lines).encode("latin-1", "replace")
        
        objects.append(f"{page_obj_idx} 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 {font_obj_idx} 0 R >> >> /MediaBox [0 0 612 792] /Contents {content_obj_idx} 0 R >>\nendobj\n")
        objects.append(f"{content_obj_idx} 0 obj\n<< /Length {len(stream_content)} >>\nstream\n{stream_content.decode('latin-1')}\nendstream\nendobj\n")

    objects.append(f"{font_obj_idx} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    pdf_bytes = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    xref_offsets = [0]
    for obj in objects:
        xref_offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj.encode("latin-1") + b"\n")

    xref_start = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for offset in xref_offsets[1:]:
        pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf_bytes.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("latin-1"))

    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"[SUCCESS] Created industrial sample PDF -> {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    generate_sample_documents()
