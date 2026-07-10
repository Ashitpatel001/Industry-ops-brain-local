#!/usr/bin/env python3
"""
scripts/seed.py
===============
Self-healing data seeding script for Ops Brain Local.
1. Checks if seed JSON files in data/seed/ and data/regulations/ are empty/missing.
   If empty, generates comprehensive industrial safety seed data (assets, WOs, incidents, failure modes, regulations).
2. Loads seed data into SQLite metadata database (data/metadata.db).
3. Constructs and serializes the NetworkX industrial knowledge graph (data/graph.pkl).

Usage:
    python scripts/seed.py
"""

import json
import logging
import os
import pickle
import sqlite3
import sys
from pathlib import Path
import networkx as nx

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("SeedData")

# Directories
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SEED_DIR = DATA_DIR / "seed"
REGS_DIR = DATA_DIR / "regulations"
DB_PATH = DATA_DIR / "metadata.db"
GRAPH_PATH = DATA_DIR / "graph.pkl"


def ensure_seed_json_files():
    """Generate realistic industrial seed data if JSON files are missing or 0 bytes."""
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    REGS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Assets
    assets_file = SEED_DIR / "assets.json"
    if not assets_file.exists() or assets_file.stat().st_size == 0:
        logger.info(f"🌱 Generating seed assets data -> {assets_file}")
        assets_data = [
            {"asset_tag": "P-204", "name": "Crude Charge Pump A", "type": "Centrifugal Pump", "criticality": "HIGH", "process_unit": "Unit-5 (CDU)", "mtbf_days": 67, "status": "WARNING", "description": "Primary feed pump for crude distillation column. History of mechanical seal failures."},
            {"asset_tag": "P-101", "name": "Reflux Pump B", "type": "Centrifugal Pump", "criticality": "MEDIUM", "process_unit": "Unit-2 (VDU)", "mtbf_days": 180, "status": "OPERATIONAL", "description": "Overhead reflux pump for vacuum tower."},
            {"asset_tag": "HX-301", "name": "Pre-Heat Exchanger Bank", "type": "Shell & Tube Exchanger", "criticality": "HIGH", "process_unit": "Unit-5 (CDU)", "mtbf_days": 240, "status": "OPERATIONAL", "description": "Crude pre-heat exchanger train. Susceptible to tube-side fouling and differential pressure buildup."},
            {"asset_tag": "V-112", "name": "High Pressure Separator Vessel", "type": "Pressure Vessel", "criticality": "HIGH", "process_unit": "Unit-3 (Hydrocracker)", "mtbf_days": 365, "status": "OPERATIONAL", "description": "3-phase separator operating at 150 bar. Requires rigorous weld inspection and relief valve testing."},
            {"asset_tag": "V-205", "name": "Refinery Blowdown Drum", "type": "Atmospheric Vessel", "criticality": "MEDIUM", "process_unit": "Unit-1 (Flare Train)", "mtbf_days": 500, "status": "OPERATIONAL", "description": "Emergency blowdown collection drum for flare headers."},
            {"asset_tag": "C-401", "name": "Make-up Gas Compressor", "type": "Reciprocating Compressor", "criticality": "HIGH", "process_unit": "Unit-3 (Hydrocracker)", "mtbf_days": 90, "status": "WARNING", "description": "High pressure hydrogen compressor. Frequent valve cage wear and vibration alerts."},
            {"asset_tag": "T-501", "name": "Atmospheric Distillation Tower", "type": "Distillation Column", "criticality": "HIGH", "process_unit": "Unit-5 (CDU)", "mtbf_days": 730, "status": "OPERATIONAL", "description": "Main atmospheric crude distillation column."},
            {"asset_tag": "B-601", "name": "Fired Heater Furnace", "type": "Fired Heater", "criticality": "HIGH", "process_unit": "Unit-5 (CDU)", "mtbf_days": 300, "status": "OPERATIONAL", "description": "Natural gas and fuel oil fired crude feed heater. Requires burner management system monitoring."},
            {"asset_tag": "P-305", "name": "Amine Circulation Pump", "type": "Centrifugal Pump", "criticality": "MEDIUM", "process_unit": "Unit-4 (SRU)", "mtbf_days": 150, "status": "OPERATIONAL", "description": "Lean amine pump for sulfur recovery unit."},
            {"asset_tag": "HX-402", "name": "Condenser Bank", "type": "Air Cooled Exchanger", "criticality": "LOW", "process_unit": "Unit-2 (VDU)", "mtbf_days": 400, "status": "OPERATIONAL", "description": "Fin-fan cooler for vacuum tower overhead vapors."}
        ]
        with open(assets_file, "w", encoding="utf-8") as f:
            json.dump(assets_data, f, indent=2)

    # 2. Failure Modes
    fmodes_file = SEED_DIR / "failure_modes.json"
    if not fmodes_file.exists() or fmodes_file.stat().st_size == 0:
        logger.info(f"🌱 Generating seed failure modes data -> {fmodes_file}")
        fmodes_data = [
            {"mode_id": "FM-001", "name": "Mechanical Seal Failure", "category": "Mechanical Wear", "description": "Leakage across pump mechanical seal faces due to thermal shock, dry running, or abrasive particulates.", "typical_cause": "Improper flushing plan (Plan 53A pressure loss) or excessive vibration.", "recommended_action": "Inspect seal cartridge, verify seal flush pressure, and check shaft alignment."},
            {"mode_id": "FM-002", "name": "Bearing Seizure / Wear", "category": "Mechanical Wear", "description": "Overheating and spalling of rolling element bearings.", "typical_cause": "Lubrication starvation, oil contamination, or misalignment.", "recommended_action": "Perform vibration spectrum analysis, flush lube oil housing, and replace bearings."},
            {"mode_id": "FM-003", "name": "Tube-side Fouling", "category": "Thermal / Flow", "description": "Accumulation of asphaltenes and inorganic deposits inside exchanger tubes.", "typical_cause": "Low tube velocity or crude incompatibility.", "recommended_action": "Schedule hydro-jetting cleanout during next turnaround; monitor differential pressure."},
            {"mode_id": "FM-004", "name": "Compressor Valve Cage Failure", "category": "Mechanical Fatigue", "description": "Cracking or sticking of suction/discharge suction valves in reciprocating compressors.", "typical_cause": "Liquid carryover in gas stream or cyclic fatigue.", "recommended_action": "Inspect suction knockout drum demister and replace valve assemblies."},
            {"mode_id": "FM-005", "name": "Atmospheric O2 Testing Failure", "category": "Safety / Compliance", "description": "Failure to perform or document atmospheric oxygen and toxic gas testing before confined space entry.", "typical_cause": "SOP procedural shortcut or uncalibrated multi-gas detector.", "recommended_action": "Enforce mandatory checklist hold-point; mandate OISD-GDN-192 compliance verification."}
        ]
        with open(fmodes_file, "w", encoding="utf-8") as f:
            json.dump(fmodes_data, f, indent=2)

    # 3. Work Orders
    wos_file = SEED_DIR / "work_orders.json"
    if not wos_file.exists() or wos_file.stat().st_size == 0:
        logger.info(f"🌱 Generating seed work orders data -> {wos_file}")
        wos_data = [
            {"wo_id": "WO-10234", "asset_tag": "P-204", "title": "Emergency Mechanical Seal Replacement", "description": "Primary mechanical seal failed causing hydrocarbons to leak into atmosphere. Unit tripped by operator. Replaced double mechanical seal cartridge.", "failure_mode": "Mechanical Seal Failure", "date_created": "2024-01-15", "status": "COMPLETED", "cost": 12500, "downtime_hours": 18},
            {"wo_id": "WO-10552", "asset_tag": "P-204", "title": "Seal Flush Plan 53A Pressure Drop Investigation", "description": "Barrier fluid pressure dropped below chamber pressure. Found micro-leak in accumulator fitting. Replaced fitting and recharged N2.", "failure_mode": "Mechanical Seal Failure", "date_created": "2024-02-28", "status": "COMPLETED", "cost": 1800, "downtime_hours": 4},
            {"wo_id": "WO-10891", "asset_tag": "P-204", "title": "Recurrent Seal Failure & Shaft Vibration Analysis", "description": "Third seal failure in 18 months. Vibration analysis indicated 4.5 mm/s RMS at 1X RPM indicating angular misalignment. Laser aligned pump and motor.", "failure_mode": "Mechanical Seal Failure", "date_created": "2024-04-10", "status": "COMPLETED", "cost": 15000, "downtime_hours": 24},
            {"wo_id": "WO-11002", "asset_tag": "HX-301", "title": "High Differential Pressure Cleanout", "description": "Tube side differential pressure exceeded 1.8 bar. Performed high pressure chemical washing and mechanical hydro-jetting.", "failure_mode": "Tube-side Fouling", "date_created": "2024-03-12", "status": "COMPLETED", "cost": 28000, "downtime_hours": 48},
            {"wo_id": "WO-11205", "asset_tag": "C-401", "title": "Suction Valve Replacement on Cylinder 2", "description": "High discharge temperature and abnormal clattering noise. Disassembled Cylinder 2 and found cracked suction valve plate. Replaced valve assembly.", "failure_mode": "Compressor Valve Cage Failure", "date_created": "2024-05-02", "status": "COMPLETED", "cost": 9500, "downtime_hours": 12},
            {"wo_id": "WO-11450", "asset_tag": "P-101", "title": "Preventive Bearing Lubrication and PM", "description": "Scheduled 6-month preventive maintenance. Sampled lube oil, checked vibration spectra (normal), and topped off synthetic oil.", "failure_mode": "Bearing Seizure / Wear", "date_created": "2024-05-20", "status": "COMPLETED", "cost": 850, "downtime_hours": 2},
            {"wo_id": "WO-11600", "asset_tag": "V-112", "title": "Annual Safety Relief Valve Testing", "description": "Removed PSV-112A and tested on bench. Pop pressure verified at 150 bar. Reinstalled with new spiral wound gaskets.", "failure_mode": "Atmospheric O2 Testing Failure", "date_created": "2024-06-01", "status": "COMPLETED", "cost": 3200, "downtime_hours": 6}
        ]
        with open(wos_file, "w", encoding="utf-8") as f:
            json.dump(wos_data, f, indent=2)

    # 4. Incidents
    inc_file = SEED_DIR / "incidents.json"
    if not inc_file.exists() or inc_file.stat().st_size == 0:
        logger.info(f"🌱 Generating seed incidents data -> {inc_file}")
        inc_data = [
            {"incident_id": "INC-2024-001", "title": "Hydrocarbon Flash Fire near P-204", "date_occurred": "2024-01-15", "severity": "HIGH", "asset_tag": "P-204", "root_cause": "Catastrophic mechanical seal blowout resulting in crude oil spray onto hot adjacent steam header.", "failure_mode": "Mechanical Seal Failure", "preventive_action": "Upgrade seal to dual pressurized cartridge (API 682 Plan 53B) and install acoustic leak detection."},
            {"incident_id": "INC-2024-002", "title": "Near-Miss Confined Space Entry at V-205", "date_occurred": "2024-03-22", "severity": "CRITICAL", "asset_tag": "V-205", "root_cause": "Contractor team attempted vessel entry without conducting atmospheric oxygen test or obtaining signed permit.", "failure_mode": "Atmospheric O2 Testing Failure", "preventive_action": "Mandatory stand-down training on OISD-GDN-192 and implementation of physical lockout hasps on vessel manways."},
            {"incident_id": "INC-2024-003", "title": "Compressor Trip on High Vibration C-401", "date_occurred": "2024-05-02", "severity": "MEDIUM", "asset_tag": "C-401", "root_cause": "Valve debris fell into cylinder bore following valve cage fatigue failure.", "failure_mode": "Compressor Valve Cage Failure", "preventive_action": "Implement ultrasonic valve monitoring and shorten valve inspection interval to 4,000 operating hours."}
        ]
        with open(inc_file, "w", encoding="utf-8") as f:
            json.dump(inc_data, f, indent=2)

    # 5. Regulations
    reg_files = {
        "oisd_116.json": [
            {"reg_id": "OISD-116-4.1", "standard": "OISD-116", "clause": "4.1", "title": "Fire Protection in Petroleum Refineries - Pump Spacing", "requirement": "Hydrocarbon handling pumps operating above 200°C shall be located at least 15 meters away from fired heaters and furnaces.", "category": "Fire Safety", "status": "ACTIVE"},
            {"reg_id": "OISD-116-7.2", "standard": "OISD-116", "clause": "7.2", "title": "Mechanical Seal Requirements", "requirement": "All centrifugal pumps handling volatile hydrocarbons (Class A and B petroleum products) must be equipped with double mechanical seals or tandem mechanical seals with appropriate barrier fluid monitoring systems.", "category": "Equipment Safety", "status": "ACTIVE"}
        ],
        "oisd_gdn192.json": [
            {"reg_id": "OISD-GDN-192-7.3.2", "standard": "OISD-GDN-192", "clause": "7.3.2", "title": "Confined Space Entry - Atmospheric Testing", "requirement": "Before any personnel enter a confined space, atmospheric testing MUST be conducted for oxygen content (must be between 19.5% and 23.5% by volume), flammable gases (< 1% LEL), and toxic gases (H2S < 10 ppm, CO < 35 ppm). Results must be recorded on the entry permit.", "category": "Life Safety", "status": "ACTIVE"},
            {"reg_id": "OISD-GDN-192-8.1", "standard": "OISD-GDN-192", "clause": "8.1", "title": "Standby Person / Hole Watch", "requirement": "A dedicated, trained standby person (hole watch) must remain outside the confined space entrance at all times while personnel are inside, equipped with reliable emergency communication.", "category": "Life Safety", "status": "ACTIVE"}
        ],
        "factory_act.json": [
            {"reg_id": "FA1948-SEC36", "standard": "Factory Act 1948", "clause": "Section 36", "title": "Precautions against dangerous fumes, gases, and dusts", "requirement": "No person shall be required or allowed to enter any chamber, tank, vat, pit, pipe, flue or other confined space in any factory in which any gas, fume, vapour or dust is likely to be present to such an extent as to involve risk to persons, unless it is provided with a manhole of adequate size or other effective means of egress and certified safe by a competent person.", "category": "Statutory Compliance", "status": "ACTIVE"},
            {"reg_id": "FA1948-SEC31", "standard": "Factory Act 1948", "clause": "Section 31", "title": "Pressure Plants and Vessels", "requirement": "If in any factory any plant or machinery or vessel is operated at a pressure above atmospheric pressure, effective measures shall be taken to ensure that the safe working pressure is not exceeded, including periodic examination and testing by a competent person at least once every 12 months.", "category": "Statutory Compliance", "status": "ACTIVE"}
        ],
        "peso.json": [
            {"reg_id": "PESO-SMPV-18", "standard": "PESO SMPV Rules", "clause": "Rule 18", "title": "Safety Relief Valves on Pressure Vessels", "requirement": "Every static pressure vessel for storage of compressed gases must be fitted with at least two safety relief valves set to discharge at a pressure not exceeding the design pressure of the vessel.", "category": "Statutory Compliance", "status": "ACTIVE"}
        ]
    }
    for filename, data in reg_files.items():
        filepath = REGS_DIR / filename
        if not filepath.exists() or filepath.stat().st_size == 0:
            logger.info(f"🌱 Generating seed regulation data -> {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)


def init_sqlite_db():
    """Initialize SQLite database with schema for assets, work orders, incidents, regulations, docs, and audit logs."""
    logger.info(f"📦 Initializing SQLite database -> {DB_PATH}")
    if DB_PATH.exists():
        DB_PATH.unlink()  # Clean rebuild during seeding

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        asset_tag TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        criticality TEXT,
        process_unit TEXT,
        mtbf_days INTEGER,
        status TEXT,
        description TEXT
    )
    """)

    # 2. Work Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS work_orders (
        wo_id TEXT PRIMARY KEY,
        asset_tag TEXT,
        title TEXT,
        description TEXT,
        failure_mode TEXT,
        date_created TEXT,
        status TEXT,
        cost REAL,
        downtime_hours REAL,
        FOREIGN KEY (asset_tag) REFERENCES assets(asset_tag)
    )
    """)

    # 3. Incidents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        title TEXT,
        date_occurred TEXT,
        severity TEXT,
        asset_tag TEXT,
        root_cause TEXT,
        failure_mode TEXT,
        preventive_action TEXT,
        FOREIGN KEY (asset_tag) REFERENCES assets(asset_tag)
    )
    """)

    # 4. Failure Modes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS failure_modes (
        mode_id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        description TEXT,
        typical_cause TEXT,
        recommended_action TEXT
    )
    """)

    # 5. Regulations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regulations (
        reg_id TEXT PRIMARY KEY,
        standard TEXT,
        clause TEXT,
        title TEXT,
        requirement TEXT,
        category TEXT,
        status TEXT
    )
    """)

    # 6. Documents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        title TEXT,
        file_path TEXT,
        doc_type TEXT,
        status TEXT,
        indexed_at TEXT
    )
    """)

    # 7. Chunks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_id TEXT PRIMARY KEY,
        doc_id TEXT,
        chunk_index INTEGER,
        text TEXT,
        section_header TEXT,
        tokens INTEGER,
        FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
    )
    """)

    # 8. Audit Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        query TEXT,
        response TEXT,
        confidence TEXT,
        backend TEXT,
        latency_ms INTEGER
    )
    """)

    conn.commit()
    return conn


def seed_sqlite_and_graph(conn: sqlite3.Connection):
    """Load JSON seed files into SQLite and build NetworkX graph."""
    cursor = conn.cursor()
    G = nx.MultiDiGraph()

    logger.info("🕸️ Populating SQLite tables and building NetworkX knowledge graph...")

    # Load Assets
    with open(SEED_DIR / "assets.json", "r", encoding="utf-8") as f:
        assets = json.load(f)
        for a in assets:
            cursor.execute("""
            INSERT OR REPLACE INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (a["asset_tag"], a["name"], a["type"], a["criticality"], a["process_unit"], a["mtbf_days"], a["status"], a["description"]))
            
            # Add Graph Nodes & Edges
            G.add_node(a["asset_tag"], type="Asset", name=a["name"], criticality=a["criticality"], mtbf=a["mtbf_days"], status=a["status"])
            G.add_node(a["process_unit"], type="ProcessUnit", name=a["process_unit"])
            G.add_edge(a["asset_tag"], a["process_unit"], relation="BELONGS_TO")

    # Load Failure Modes
    with open(SEED_DIR / "failure_modes.json", "r", encoding="utf-8") as f:
        fmodes = json.load(f)
        for fm in fmodes:
            cursor.execute("""
            INSERT OR REPLACE INTO failure_modes VALUES (?, ?, ?, ?, ?, ?)
            """, (fm["mode_id"], fm["name"], fm["category"], fm["description"], fm["typical_cause"], fm["recommended_action"]))
            
            G.add_node(fm["name"], type="FailureMode", mode_id=fm["mode_id"], category=fm["category"], action=fm["recommended_action"])

    # Load Work Orders
    with open(SEED_DIR / "work_orders.json", "r", encoding="utf-8") as f:
        wos = json.load(f)
        for wo in wos:
            cursor.execute("""
            INSERT OR REPLACE INTO work_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (wo["wo_id"], wo["asset_tag"], wo["title"], wo["description"], wo["failure_mode"], wo["date_created"], wo["status"], wo["cost"], wo["downtime_hours"]))
            
            G.add_node(wo["wo_id"], type="WorkOrder", title=wo["title"], date=wo["date_created"], cost=wo["cost"])
            G.add_edge(wo["wo_id"], wo["asset_tag"], relation="PERFORMED_ON")
            if wo.get("failure_mode"):
                G.add_edge(wo["asset_tag"], wo["failure_mode"], relation="HAS_FAILURE_MODE")
                G.add_edge(wo["wo_id"], wo["failure_mode"], relation="ADDRESSES_FAILURE")

    # Load Incidents
    with open(SEED_DIR / "incidents.json", "r", encoding="utf-8") as f:
        incidents = json.load(f)
        for inc in incidents:
            cursor.execute("""
            INSERT OR REPLACE INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (inc["incident_id"], inc["title"], inc["date_occurred"], inc["severity"], inc["asset_tag"], inc["root_cause"], inc["failure_mode"], inc["preventive_action"]))
            
            G.add_node(inc["incident_id"], type="Incident", title=inc["title"], severity=inc["severity"], date=inc["date_occurred"])
            G.add_edge(inc["incident_id"], inc["asset_tag"], relation="OCCURRED_ON")
            if inc.get("failure_mode"):
                G.add_edge(inc["incident_id"], inc["failure_mode"], relation="CAUSED_BY")

    # Load Regulations
    for reg_file in REGS_DIR.glob("*.json"):
        with open(reg_file, "r", encoding="utf-8") as f:
            regs = json.load(f)
            for r in regs:
                cursor.execute("""
                INSERT OR REPLACE INTO regulations VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (r["reg_id"], r["standard"], r["clause"], r["title"], r["requirement"], r["category"], r["status"]))
                
                G.add_node(r["reg_id"], type="Regulation", standard=r["standard"], clause=r["clause"], title=r["title"])

    conn.commit()

    # Save NetworkX Graph
    logger.info(f"💾 Saving NetworkX graph ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges) -> {GRAPH_PATH}")
    with open(GRAPH_PATH, "wb") as f:
        pickle.dump(G, f)

    logger.info("✅ Seeding complete! Database and Knowledge Graph ready.")


def main():
    logger.info("==========================================================================")
    logger.info("🌱 OPS BRAIN LOCAL — INDUSTRIAL DATABASE & GRAPH SEEDER")
    logger.info("==========================================================================")
    
    ensure_seed_json_files()
    conn = init_sqlite_db()
    seed_sqlite_and_graph(conn)
    conn.close()
    
    logger.info("🎉 All seed operations completed successfully!")


if __name__ == "__main__":
    main()
