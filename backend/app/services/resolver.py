import re
from typing import List, Optional, Tuple, Dict
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from backend.app.models import MedicineCatalogue, BrandMapping
from backend.app.schemas import MedicineResolutionResult, ResolvedMedicineCandidate

# Common salt / formulation suffixes to normalize out during matching
CLEANUP_SUFFIXES = [
    r'\bhydrochloride\b', r'\bhcl\b', r'\bsodium\b', r'\bpotassium\b',
    r'\bcalcium\b', r'\btartrate\b', r'\bsuccinate\b', r'\bbesylate\b',
    r'\bhydrate\b', r'\bdihydrate\b', r'\bmonohydrate\b', r'\bmg\b',
    r'\bml\b', r'\btablet\b', r'\btab\b', r'\bcapsule\b', r'\bcap\b',
    r'\ber\b', r'\bxr\b', r'\bsr\b', r'\bcr\b', r'\boral\b'
]

def normalize_text(text: str) -> str:
    """Normalize text by lowercasing, stripping punctuation, dosage numbers, and formulation suffixes."""
    if not text:
        return ""
    cleaned = text.lower().strip()
    # Strip standalone numbers with or without units (e.g., 500mg, 10 mg)
    cleaned = re.sub(r'\b\d+(\.\d+)?\s*(mg|mcg|g|ml|meq)?\b', '', cleaned)
    # Strip common suffixes
    for suffix in CLEANUP_SUFFIXES:
        cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
    # Strip non-alphanumeric except spaces and hyphens
    cleaned = re.sub(r'[^a-z0-9\s-]', ' ', cleaned)
    # Collapse multiple whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

class MedicineResolver:
    def __init__(self, db: Session):
        self.db = db
        self._load_cache()

    def _load_cache(self):
        """Preload medicines and brand mappings into memory for millisecond resolution."""
        medicines = self.db.query(MedicineCatalogue).all()
        brands = self.db.query(BrandMapping).all()

        self.generic_map: Dict[str, MedicineCatalogue] = {} # norm_name -> med
        self.brand_map: Dict[str, BrandMapping] = {} # norm_name -> brand
        self.synonym_map: Dict[str, str] = {} # norm_syn -> generic_name
        self.search_corpus: List[Tuple[str, str, str]] = [] # (normalized_name, target_type, original_name)

        for med in medicines:
            norm_gen = normalize_text(med.generic_name)
            self.generic_map[norm_gen] = med
            self.search_corpus.append((norm_gen, "generic", med.generic_name))

            for syn in (med.synonyms or []):
                norm_syn = normalize_text(syn)
                if norm_syn:
                    self.synonym_map[norm_syn] = med.generic_name
                    self.search_corpus.append((norm_syn, "synonym", syn))

            for misspelling in (med.common_misspellings or []):
                norm_mis = normalize_text(misspelling)
                if norm_mis:
                    self.synonym_map[norm_mis] = med.generic_name
                    self.search_corpus.append((norm_mis, "misspelling", misspelling))

        for bm in brands:
            norm_brand = normalize_text(bm.brand_name)
            self.brand_map[norm_brand] = bm
            self.search_corpus.append((norm_brand, "brand", bm.brand_name))

    def resolve(self, raw_input: str) -> MedicineResolutionResult:
        """Execute multi-tier deterministic and fuzzy medicine name resolution."""
        cleaned = normalize_text(raw_input)
        if not cleaned:
            return MedicineResolutionResult(
                original_input=raw_input,
                match_method="unresolved",
                match_score=0.0,
                confidence_level="UNRESOLVED"
            )

        # Tier 1: Exact Generic Match
        if cleaned in self.generic_map:
            med = self.generic_map[cleaned]
            return MedicineResolutionResult(
                original_input=raw_input,
                resolved_generic=med.generic_name,
                brand_name=None,
                active_ingredients=med.active_ingredients or [med.generic_name],
                therapeutic_class=med.therapeutic_class,
                match_score=100.0,
                match_method="exact_generic",
                is_ambiguous=False,
                requires_human_review=False,
                confidence_level="HIGH",
                candidates=[
                    ResolvedMedicineCandidate(
                        generic_name=med.generic_name,
                        brand_name=None,
                        active_ingredients=med.active_ingredients or [med.generic_name],
                        therapeutic_class=med.therapeutic_class,
                        match_score=100.0,
                        match_method="exact_generic",
                        is_ambiguous=False,
                        standard_dosing=med.standard_dosing
                    )
                ]
            )

        # Tier 2: Exact Brand Match
        if cleaned in self.brand_map:
            bm = self.brand_map[cleaned]
            med = self.generic_map.get(normalize_text(bm.generic_name))
            th_class = med.therapeutic_class if med else "Verified Pharmaceutical Brand"
            return MedicineResolutionResult(
                original_input=raw_input,
                resolved_generic=bm.generic_name,
                brand_name=bm.brand_name,
                active_ingredients=bm.active_ingredients or [bm.generic_name],
                therapeutic_class=th_class,
                match_score=100.0,
                match_method="exact_brand",
                is_ambiguous=False,
                requires_human_review=False,
                confidence_level="HIGH",
                candidates=[
                    ResolvedMedicineCandidate(
                        generic_name=bm.generic_name,
                        brand_name=bm.brand_name,
                        active_ingredients=bm.active_ingredients or [bm.generic_name],
                        therapeutic_class=th_class,
                        match_score=100.0,
                        match_method="exact_brand",
                        is_ambiguous=False,
                        standard_dosing=med.standard_dosing if med else None
                    )
                ]
            )

        # Tier 3: Verified Synonym / Catalogue Misspelling
        if cleaned in self.synonym_map:
            gen_target = self.synonym_map[cleaned]
            med = self.generic_map.get(normalize_text(gen_target))
            if med:
                return MedicineResolutionResult(
                    original_input=raw_input,
                    resolved_generic=med.generic_name,
                    brand_name=None,
                    active_ingredients=med.active_ingredients or [med.generic_name],
                    therapeutic_class=med.therapeutic_class,
                    match_score=98.0,
                    match_method="synonym",
                    is_ambiguous=False,
                    requires_human_review=False,
                    confidence_level="HIGH",
                    candidates=[
                        ResolvedMedicineCandidate(
                            generic_name=med.generic_name,
                            brand_name=None,
                            active_ingredients=med.active_ingredients or [med.generic_name],
                            therapeutic_class=med.therapeutic_class,
                            match_score=98.0,
                            match_method="synonym",
                            is_ambiguous=False,
                            standard_dosing=med.standard_dosing
                        )
                    ]
                )

        # Tier 4: Fuzzy String Matching with RapidFuzz
        corpus_strings = [item[0] for item in self.search_corpus]
        fuzzy_matches = process.extract(
            cleaned,
            corpus_strings,
            scorer=fuzz.token_sort_ratio,
            limit=5
        )

        candidate_list: List[ResolvedMedicineCandidate] = []
        seen_generics = set()

        for match_str, score, idx in fuzzy_matches:
            if score < 60.0:
                continue
            item = self.search_corpus[idx]
            match_type = item[1]
            orig_name = item[2]

            # Resolve to generic
            if match_type in ("generic", "synonym", "misspelling"):
                if match_type == "generic":
                    med_obj = self.generic_map.get(match_str)
                else:
                    gen_name = self.synonym_map.get(match_str, "")
                    med_obj = self.generic_map.get(normalize_text(gen_name))
                if med_obj and med_obj.generic_name not in seen_generics:
                    seen_generics.add(med_obj.generic_name)
                    candidate_list.append(ResolvedMedicineCandidate(
                        generic_name=med_obj.generic_name,
                        brand_name=None,
                        active_ingredients=med_obj.active_ingredients or [med_obj.generic_name],
                        therapeutic_class=med_obj.therapeutic_class,
                        match_score=round(score, 1),
                        match_method=f"fuzzy_{match_type}",
                        is_ambiguous=False,
                        standard_dosing=med_obj.standard_dosing
                    ))
            elif match_type == "brand":
                bm = self.brand_map.get(match_str)
                if bm and bm.generic_name not in seen_generics:
                    seen_generics.add(bm.generic_name)
                    med_obj = self.generic_map.get(normalize_text(bm.generic_name))
                    th = med_obj.therapeutic_class if med_obj else "Verified Brand"
                    candidate_list.append(ResolvedMedicineCandidate(
                        generic_name=bm.generic_name,
                        brand_name=bm.brand_name,
                        active_ingredients=bm.active_ingredients or [bm.generic_name],
                        therapeutic_class=th,
                        match_score=round(score, 1),
                        match_method="fuzzy_brand",
                        is_ambiguous=False,
                        standard_dosing=med_obj.standard_dosing if med_obj else None
                    ))

        if not candidate_list:
            return MedicineResolutionResult(
                original_input=raw_input,
                match_method="unresolved",
                match_score=0.0,
                is_ambiguous=False,
                requires_human_review=True,
                confidence_level="UNRESOLVED",
                candidates=[]
            )

        top_cand = candidate_list[0]

        # Ambiguity Checking:
        # 1. Multiple top candidates with very close score (difference <= 6%)
        # 2. Or top score is between 65% and 84% (requires clinician confirmation before running checks)
        is_ambiguous = False
        requires_review = False
        confidence = "HIGH"

        if len(candidate_list) > 1:
            diff = top_cand.match_score - candidate_list[1].match_score
            if diff <= 6.0 and top_cand.match_score < 96.0:
                is_ambiguous = True
                requires_review = True
                confidence = "MEDIUM"

        if top_cand.match_score < 85.0:
            requires_review = True
            confidence = "MEDIUM" if top_cand.match_score >= 70.0 else "LOW"

        # If ambiguous, mark all candidates as ambiguous
        if is_ambiguous:
            for c in candidate_list:
                c.is_ambiguous = True

        return MedicineResolutionResult(
            original_input=raw_input,
            resolved_generic=top_cand.generic_name if not is_ambiguous else None,
            brand_name=top_cand.brand_name if not is_ambiguous else None,
            active_ingredients=top_cand.active_ingredients if not is_ambiguous else [],
            therapeutic_class=top_cand.therapeutic_class if not is_ambiguous else None,
            match_score=top_cand.match_score,
            match_method="ambiguous" if is_ambiguous else top_cand.match_method,
            is_ambiguous=is_ambiguous,
            candidates=candidate_list,
            requires_human_review=requires_review,
            confidence_level=confidence
        )
