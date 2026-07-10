"""
ingestion/extractor.py
======================
Production-grade entity extractor tailored for industrial plant environments.
Combines spaCy NLP models with specialized industrial regex patterns to extract:
- Equipment / Asset Tags (P-204, HX-301, V-112, C-401)
- Regulatory References (OISD-116, OISD-GDN-192, Factory Act 1948, PESO)
- Failure Modes & Keywords (seal failure, bearing wear, fouling, vibration)
- Dates & Temporal markers
- Personnel & Industrial Roles (Standby Person, Hole Watch, Operator)
"""

import logging
import re
from typing import Any, Dict, List, Set

logger = logging.getLogger("EntityExtractor")

# Common English words/abbreviations to ignore when matching asset tags
IGNORE_TAGS: Set[str] = {
    "THE", "FOR", "AND", "NOT", "YES", "OUT", "SET", "NEW", "OLD", "REV",
    "ISO", "STD", "REF", "SEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "ALL", "MAX", "MIN", "AVG",
}


_nlp_singleton = None
_nlp_attempted = False

def _get_spacy_model():
    global _nlp_singleton, _nlp_attempted
    if not _nlp_attempted:
        _nlp_attempted = True
        try:
            import spacy
            logger.info("Loading spaCy NLP model ('en_core_web_sm') singleton...")
            _nlp_singleton = spacy.load("en_core_web_sm")
            logger.info("spaCy NLP model loaded successfully.")
        except ImportError as e:
            logger.warning(f"spaCy not installed ({e}). Relying on high-precision regex extraction.")
        except OSError as e:
            logger.warning(f"spaCy model 'en_core_web_sm' not found ({e}). Relying on regex extraction.")
        except Exception as e:
            logger.warning(f"Error loading spaCy ({e}). Relying on regex extraction.")
    return _nlp_singleton


class EntityExtractor:
    """
    Industrial entity extractor combining spaCy NLP and specialized regular expressions.
    Runs 100% offline without external API dependencies.
    """

    def __init__(self):
        self._nlp = _get_spacy_model()

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract industrial entities from raw text.

        Args:
            text (str): Document or chunk text.

        Returns:
            Dict containing sorted, deduplicated lists of extracted entities:
            - asset_tags (List[str])
            - regulatory_refs (List[str])
            - failure_keywords (List[str])
            - dates (List[str])
            - persons (List[str])
            - total_entities (int)
        """
        if not text or not text.strip():
            return {
                "asset_tags": [],
                "regulatory_refs": [],
                "failure_keywords": [],
                "dates": [],
                "persons": [],
                "total_entities": 0,
            }

        asset_tags: Set[str] = set()
        reg_refs: Set[str] = set()
        failure_keywords: Set[str] = set()
        dates: Set[str] = set()
        persons: Set[str] = set()

        # 1. Regex Extraction — Equipment / Asset Tags (e.g., P-204, HX-301, V-112, C-401, PSV-112A)
        tag_matches = re.findall(r"\b([A-Z]{1,3}[-]?\d{2,4}[A-Z]?)\b", text)
        for tag in tag_matches:
            clean_tag = tag.upper().strip()
            # Filter out non-asset tags and standalone numbers
            if clean_tag not in IGNORE_TAGS and not clean_tag.isdigit() and len(clean_tag) >= 3:
                # Ensure it has at least one letter and one digit
                if any(c.isalpha() for c in clean_tag) and any(c.isdigit() for c in clean_tag):
                    asset_tags.add(clean_tag)

        # 2. Regex Extraction — Regulatory References
        reg_matches = re.findall(
            r"\b(OISD[-\s]?(?:GDN[-\s]?)?\d+(?:-\d+(?:\.\d+)?)?|Factory\s+Act(?:\s+1948)?|PESO|IS:\s?\d+|API\s+682|ASME\s+Sec\s+[IVX]+)\b",
            text,
            flags=re.IGNORECASE,
        )
        for reg in reg_matches:
            reg_refs.add(re.sub(r"\s+", " ", reg).upper().strip())

        # 3. Regex Extraction — Industrial Failure Modes & Keywords
        failure_pattern = (
            r"\b(seal\s+failure|bearing\s+(?:seizure|wear|failure)|tube-?side\s+fouling|fouling|vibration|"
            r"leak(?:age)?|corrosion|fatigue|blowout|crack(?:ing)?|misalignment|suction\s+valve|pressure\s+drop|"
            r"dry\s+running|spalling|overheating|clattering|liquid\s+carryover|o2\s+test(?:ing)?\s+failure|"
            r"tripped|breakdown|micro-?leak|starvation)\b"
        )
        failure_matches = re.findall(failure_pattern, text, flags=re.IGNORECASE)
        for fk in failure_matches:
            failure_keywords.add(fk.lower().strip())

        # 4. Regex Extraction — Dates
        date_matches = re.findall(
            r"\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{2}[-/]\d{2}[-/]\d{4})\b",
            text,
            flags=re.IGNORECASE,
        )
        for d in date_matches:
            dates.add(d.strip())

        # 5. Regex Extraction — Industrial Roles / Standby Personnel
        role_matches = re.findall(
            r"\b(Standby\s+Person|Hole\s+Watch|Operator|Technician|Supervisor|Inspector|Safety\s+Officer|Engineer)\b",
            text,
            flags=re.IGNORECASE,
        )
        for role in role_matches:
            persons.add(role.title().strip())

        # 6. spaCy NLP Extraction (if available) for Persons and Dates
        if self._nlp:
            try:
                doc = self._nlp(text[:100000])  # Cap at 100k chars for speed
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name = ent.text.strip()
                        if len(name) > 2 and not any(c.isdigit() for c in name):
                            persons.add(name)
                    elif ent.label_ == "DATE":
                        d_text = ent.text.strip()
                        if any(c.isdigit() for c in d_text) and len(d_text) > 3:
                            dates.add(d_text)
            except Exception as e:
                logger.debug(f"spaCy NLP extraction skipped: {e}")

        # Compile sorted lists
        result = {
            "asset_tags": sorted(list(asset_tags)),
            "regulatory_refs": sorted(list(reg_refs)),
            "failure_keywords": sorted(list(failure_keywords)),
            "dates": sorted(list(dates)),
            "persons": sorted(list(persons)),
        }
        result["total_entities"] = sum(len(v) for v in result.values() if isinstance(v, list))

        logger.debug(f"Extracted {result['total_entities']} entities from text.")
        return result
