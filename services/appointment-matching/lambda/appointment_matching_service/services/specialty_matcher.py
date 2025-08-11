"""
Specialty Matcher service with fuzzy matching for the Appointment Matching Service.
"""

from decimal import Decimal
from typing import List, Dict, Set
from difflib import SequenceMatcher

from ..models.analysis_results import SpecialtyMatch
from ..utils.helpers import generate_uuid, get_current_utc_datetime, setup_logging
from ..utils.exceptions import MatchingError, ValidationError


class SpecialtyMatcher:
    """Service for matching symptoms to medical specialties using fuzzy matching."""
    
    def __init__(self):
        self.id = generate_uuid()
        self.fuzzy_threshold = Decimal('0.8')
        self.exact_match_weight = Decimal('1.0')
        self.fuzzy_match_weight = Decimal('0.7')
        self.logger = setup_logging("SpecialtyMatcher")
        
        # Specialty keywords mapping (expanded for demo)
        self.specialty_keywords = {
            'cardiology': [
                'heart', 'chest', 'cardiac', 'blood', 'pressure', 'pulse', 'arrhythmia',
                'palpitation', 'angina', 'coronary', 'cardiovascular', 'hypertension'
            ],
            'dermatology': [
                'skin', 'rash', 'itching', 'acne', 'mole', 'eczema', 'psoriasis',
                'dermatitis', 'hives', 'lesion', 'pigmentation', 'allergic'
            ],
            'neurology': [
                'headache', 'dizziness', 'numbness', 'tingling', 'seizure', 'migraine',
                'neurological', 'brain', 'nerve', 'paralysis', 'tremor', 'memory'
            ],
            'gastroenterology': [
                'stomach', 'nausea', 'vomiting', 'diarrhea', 'constipation', 'abdominal',
                'digestive', 'bowel', 'gastric', 'intestinal', 'acid', 'reflux'
            ],
            'orthopedics': [
                'bone', 'joint', 'muscle', 'back', 'knee', 'shoulder', 'fracture',
                'sprain', 'arthritis', 'osteoporosis', 'ligament', 'tendon'
            ],
            'pulmonology': [
                'lung', 'cough', 'breath', 'shortness', 'chest', 'respiratory',
                'asthma', 'bronchitis', 'pneumonia', 'wheezing', 'sputum'
            ],
            'ophthalmology': [
                'eye', 'vision', 'sight', 'blind', 'blurry', 'double', 'glaucoma',
                'cataract', 'retina', 'cornea', 'pupil', 'iris'
            ],
            'otolaryngology': [
                'ear', 'nose', 'throat', 'hearing', 'sinus', 'tonsil', 'voice',
                'hoarse', 'deaf', 'tinnitus', 'vertigo', 'nasal'
            ],
            'general': [
                'fever', 'fatigue', 'weakness', 'pain', 'ache', 'tired', 'malaise',
                'general', 'overall', 'systemic', 'flu', 'cold'
            ]
        }
        
        # Keyword synonyms for fuzzy matching
        self.keyword_synonyms = {
            'pain': ['ache', 'hurt', 'sore', 'discomfort', 'tender'],
            'fever': ['temperature', 'hot', 'feverish', 'pyrexia'],
            'tired': ['fatigue', 'exhausted', 'weary', 'weakness'],
            'nausea': ['sick', 'queasy', 'nauseated', 'stomach'],
            'headache': ['head', 'migraine', 'cephalgia'],
            'shortness': ['difficulty', 'trouble', 'hard'],
            'breath': ['breathing', 'respiratory', 'air']
        }
        
        self.created_at = get_current_utc_datetime()
        self.updated_at = get_current_utc_datetime()
    
    def match_specialties(self, keywords: List[str]) -> List[SpecialtyMatch]:
        """Match keywords to medical specialties using fuzzy matching."""
        try:
            self.logger.info(f"Matching specialties for {len(keywords)} keywords")
            
            if not keywords:
                return []
            
            specialty_matches = []
            
            for specialty_name, specialty_keywords in self.specialty_keywords.items():
                match = self._calculate_specialty_match(keywords, specialty_name, specialty_keywords)
                if match.match_score > Decimal('0.0'):
                    specialty_matches.append(match)
            
            # Rank specialties by match score
            ranked_matches = self.rank_specialties(specialty_matches)
            
            self.logger.info(f"Found {len(ranked_matches)} specialty matches")
            return ranked_matches
            
        except Exception as e:
            self.logger.error(f"Specialty matching failed: {e}")
            raise MatchingError(f"Failed to match specialties: {e}")
    
    def calculate_exact_matches(self, keywords: List[str], specialty_keywords: List[str]) -> int:
        """Calculate exact keyword matches."""
        keyword_set = {kw.lower() for kw in keywords}
        specialty_set = {kw.lower() for kw in specialty_keywords}
        return len(keyword_set.intersection(specialty_set))
    
    def calculate_fuzzy_matches(self, keywords: List[str], specialty_keywords: List[str]) -> Decimal:
        """Calculate fuzzy matches using similarity scoring."""
        fuzzy_score = Decimal('0.0')
        fuzzy_count = 0
        
        for keyword in keywords:
            best_similarity = 0.0
            
            # Check direct similarity
            for specialty_keyword in specialty_keywords:
                similarity = self._calculate_similarity(keyword.lower(), specialty_keyword.lower())
                if similarity >= float(self.fuzzy_threshold):
                    best_similarity = max(best_similarity, similarity)
            
            # Check synonym similarity
            if keyword.lower() in self.keyword_synonyms:
                for synonym in self.keyword_synonyms[keyword.lower()]:
                    for specialty_keyword in specialty_keywords:
                        similarity = self._calculate_similarity(synonym, specialty_keyword.lower())
                        if similarity >= float(self.fuzzy_threshold):
                            best_similarity = max(best_similarity, similarity)
            
            if best_similarity > 0:
                fuzzy_score += Decimal(str(best_similarity))
                fuzzy_count += 1
        
        return fuzzy_score if fuzzy_count == 0 else fuzzy_score / Decimal(str(fuzzy_count))
    
    def rank_specialties(self, matches: List[SpecialtyMatch]) -> List[SpecialtyMatch]:
        """Rank specialties by match score."""
        return sorted(matches, key=lambda m: m.match_score, reverse=True)
    
    def update_fuzzy_threshold(self, threshold: Decimal) -> None:
        """Update fuzzy matching threshold."""
        if not self.validate_fuzzy_threshold(threshold):
            raise ValidationError("Fuzzy threshold must be between 0.0 and 1.0")
        
        self.fuzzy_threshold = threshold
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Updated fuzzy threshold to {threshold}")
    
    def update_match_weights(self, exact_weight: Decimal, fuzzy_weight: Decimal) -> None:
        """Update match weights."""
        if not self.validate_match_weights(exact_weight, fuzzy_weight):
            raise ValidationError("Match weights must be between 0.0 and 1.0")
        
        self.exact_match_weight = exact_weight
        self.fuzzy_match_weight = fuzzy_weight
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Updated match weights: exact={exact_weight}, fuzzy={fuzzy_weight}")
    
    def add_specialty_keywords(self, specialty_name: str, keywords: List[str]) -> None:
        """Add keywords for a specialty."""
        if not self.validate_specialty_keywords(specialty_name, keywords):
            raise ValidationError("Invalid specialty name or keywords")
        
        specialty_key = specialty_name.lower()
        if specialty_key not in self.specialty_keywords:
            self.specialty_keywords[specialty_key] = []
        
        # Add new keywords (avoid duplicates)
        existing_keywords = set(self.specialty_keywords[specialty_key])
        new_keywords = [kw.lower() for kw in keywords if kw.lower() not in existing_keywords]
        self.specialty_keywords[specialty_key].extend(new_keywords)
        
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Added {len(new_keywords)} keywords to {specialty_name}")
    
    def add_keyword_synonyms(self, keyword: str, synonyms: List[str]) -> None:
        """Add synonyms for a keyword."""
        if not keyword or not synonyms:
            raise ValidationError("Keyword and synonyms are required")
        
        keyword_key = keyword.lower()
        if keyword_key not in self.keyword_synonyms:
            self.keyword_synonyms[keyword_key] = []
        
        # Add new synonyms (avoid duplicates)
        existing_synonyms = set(self.keyword_synonyms[keyword_key])
        new_synonyms = [syn.lower() for syn in synonyms if syn.lower() not in existing_synonyms]
        self.keyword_synonyms[keyword_key].extend(new_synonyms)
        
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Added {len(new_synonyms)} synonyms for {keyword}")
    
    def validate_fuzzy_threshold(self, threshold: Decimal) -> bool:
        """Validate fuzzy threshold."""
        return Decimal('0.0') <= threshold <= Decimal('1.0')
    
    def validate_match_weights(self, exact_weight: Decimal, fuzzy_weight: Decimal) -> bool:
        """Validate match weights."""
        return (Decimal('0.0') <= exact_weight <= Decimal('1.0') and
                Decimal('0.0') <= fuzzy_weight <= Decimal('1.0'))
    
    def validate_specialty_keywords(self, specialty_name: str, keywords: List[str]) -> bool:
        """Validate specialty keywords."""
        return (bool(specialty_name) and 
                isinstance(keywords, list) and 
                len(keywords) > 0 and
                all(isinstance(kw, str) and kw.strip() for kw in keywords))
    
    def _calculate_specialty_match(self, keywords: List[str], specialty_name: str, 
                                 specialty_keywords: List[str]) -> SpecialtyMatch:
        """Calculate match score for a specialty."""
        # Calculate exact matches
        exact_matches = self.calculate_exact_matches(keywords, specialty_keywords)
        
        # Calculate fuzzy matches
        fuzzy_score = self.calculate_fuzzy_matches(keywords, specialty_keywords)
        fuzzy_matches = int(fuzzy_score * 10)  # Convert to approximate count
        
        # Calculate overall match score
        exact_contribution = Decimal(str(exact_matches)) * self.exact_match_weight
        fuzzy_contribution = fuzzy_score * self.fuzzy_match_weight
        
        # Normalize by total possible matches
        max_possible_matches = len(keywords)
        if max_possible_matches > 0:
            match_score = (exact_contribution + fuzzy_contribution) / Decimal(str(max_possible_matches))
        else:
            match_score = Decimal('0.0')
        
        # Ensure score is between 0 and 1
        match_score = min(match_score, Decimal('1.0'))
        
        # Find matched keywords
        matched_keywords = self._find_matched_keywords(keywords, specialty_keywords)
        
        return SpecialtyMatch(
            specialty_id=generate_uuid(),  # In real implementation, this would be actual specialty ID
            specialty_name=specialty_name,
            match_score=match_score,
            exact_matches=exact_matches,
            fuzzy_matches=fuzzy_matches,
            matched_keywords=matched_keywords
        )
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _find_matched_keywords(self, keywords: List[str], specialty_keywords: List[str]) -> List[str]:
        """Find which keywords matched for this specialty."""
        matched = []
        keyword_set = {kw.lower() for kw in keywords}
        specialty_set = {kw.lower() for kw in specialty_keywords}
        
        # Exact matches
        exact_matches = keyword_set.intersection(specialty_set)
        matched.extend(exact_matches)
        
        # Fuzzy matches
        for keyword in keywords:
            if keyword.lower() not in exact_matches:
                for specialty_keyword in specialty_keywords:
                    if self._calculate_similarity(keyword.lower(), specialty_keyword.lower()) >= float(self.fuzzy_threshold):
                        matched.append(keyword.lower())
                        break
        
        return list(set(matched))  # Remove duplicates