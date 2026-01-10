"""
Field Classification Module for Journal Categorization

This module implements the OECD Fields of Science and Technology classification
system with 6 major fields and 42 sub-fields. It provides multiple classification
methods including keyword-based, topic-based, and ISSN-based classification.

OECD Classification Structure:
1. Natural Sciences (1.1-1.7)
2. Engineering and Technology (2.1-2.11)
3. Medical and Health Sciences (3.1-3.5)
4. Agricultural Sciences (4.1-4.5)
5. Social Sciences (5.1-5.9)
6. Humanities (6.1-6.5)

Author: Scholar Extension Team
Date: January 10, 2026
"""

from typing import List, Dict, Tuple, Optional, Set
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FieldClassifier:
    """
    Classifier for journal field categorization using OECD standards.

    Supports multiple classification methods:
    - Journal name keyword matching
    - OpenAlex topic classification
    - ISSN database lookup
    - Multi-field assignments with confidence scoring
    """

    # OECD Field Structure: Major Fields (6 categories)
    MAJOR_FIELDS = {
        '1': 'Natural Sciences',
        '2': 'Engineering and Technology',
        '3': 'Medical and Health Sciences',
        '4': 'Agricultural Sciences',
        '5': 'Social Sciences',
        '6': 'Humanities'
    }

    # OECD Sub-fields (42 categories)
    SUB_FIELDS = {
        # 1. Natural Sciences
        '1.1': 'Mathematics',
        '1.2': 'Computer and information sciences',
        '1.3': 'Physical sciences',
        '1.4': 'Chemical sciences',
        '1.5': 'Earth and related environmental sciences',
        '1.6': 'Biological sciences',
        '1.7': 'Other natural sciences',

        # 2. Engineering and Technology
        '2.1': 'Civil engineering',
        '2.2': 'Electrical, electronic, information engineering',
        '2.3': 'Mechanical engineering',
        '2.4': 'Chemical engineering',
        '2.5': 'Materials engineering',
        '2.6': 'Medical engineering',
        '2.7': 'Environmental engineering',
        '2.8': 'Environmental biotechnology',
        '2.9': 'Industrial biotechnology',
        '2.10': 'Nano-technology',
        '2.11': 'Other engineering',

        # 3. Medical and Health Sciences
        '3.1': 'Basic medicine',
        '3.2': 'Clinical medicine',
        '3.3': 'Health sciences',
        '3.4': 'Medical biotechnology',
        '3.5': 'Other medical sciences',

        # 4. Agricultural Sciences
        '4.1': 'Agriculture, forestry, fisheries',
        '4.2': 'Animal and dairy science',
        '4.3': 'Veterinary science',
        '4.4': 'Agricultural biotechnology',
        '4.5': 'Other agricultural sciences',

        # 5. Social Sciences
        '5.1': 'Psychology',
        '5.2': 'Economics and business',
        '5.3': 'Educational sciences',
        '5.4': 'Sociology',
        '5.5': 'Law',
        '5.6': 'Political science',
        '5.7': 'Social and economic geography',
        '5.8': 'Media and communications',
        '5.9': 'Other social sciences',

        # 6. Humanities
        '6.1': 'History and archaeology',
        '6.2': 'Languages and literature',
        '6.3': 'Philosophy, ethics, religion',
        '6.4': 'Arts',
        '6.5': 'Other humanities'
    }

    # Comprehensive keyword mappings for each sub-field
    FIELD_KEYWORDS = {
        # Natural Sciences
        '1.1': ['mathematics', 'mathematical', 'algebra', 'geometry', 'calculus',
                'statistics', 'statistical', 'probability', 'topology', 'number theory',
                'discrete math', 'applied mathematics', 'pure mathematics'],

        '1.2': ['computer science', 'computing', 'informatics', 'software', 'algorithm',
                'programming', 'data science', 'artificial intelligence', 'machine learning',
                'information technology', 'cybernetics', 'computational', 'database',
                'information systems', 'AI', 'data mining', 'neural network', 'pattern analysis',
                'pattern recognition', 'machine intelligence', 'computer vision', 'deep learning'],

        '1.3': ['physics', 'physical', 'quantum', 'astronomy', 'astrophysics',
                'cosmology', 'optics', 'mechanics', 'thermodynamics', 'relativity',
                'particle physics', 'condensed matter', 'atomic', 'molecular physics',
                'nuclear physics', 'plasma physics', 'acoustics', 'photonics'],

        '1.4': ['chemistry', 'chemical', 'biochemistry', 'organic chemistry',
                'inorganic chemistry', 'analytical chemistry', 'physical chemistry',
                'polymer chemistry', 'catalysis', 'crystallography', 'electrochemistry',
                'photochemistry', 'molecular chemistry', 'chemical analysis'],

        '1.5': ['geology', 'geoscience', 'earth science', 'environmental science',
                'meteorology', 'climatology', 'oceanography', 'hydrology', 'geography',
                'geophysics', 'mineralogy', 'paleontology', 'volcanology', 'seismology',
                'atmospheric science', 'climate', 'geochemistry', 'soil science'],

        '1.6': ['biology', 'biological', 'life sciences', 'ecology', 'zoology',
                'botany', 'genetics', 'microbiology', 'molecular biology', 'cell biology',
                'evolutionary biology', 'developmental biology', 'neuroscience',
                'biophysics', 'marine biology', 'biotechnology', 'genomics', 'proteomics'],

        '1.7': ['natural sciences', 'interdisciplinary science', 'science general'],

        # Engineering and Technology
        '2.1': ['civil engineering', 'structural engineering', 'construction',
                'geotechnical', 'hydraulic engineering', 'transportation engineering',
                'infrastructure', 'building', 'architecture engineering'],

        '2.2': ['electrical engineering', 'electronic', 'electronics', 'telecommunications',
                'signal processing', 'circuit', 'power systems', 'control systems',
                'microelectronics', 'robotics', 'automation', 'embedded systems',
                'information engineering', 'wireless', 'optical communication', 'IEEE',
                'transactions', 'semiconductor', 'VLSI', 'communication systems'],

        '2.3': ['mechanical engineering', 'mechanics', 'manufacturing', 'automotive',
                'aerospace', 'aeronautical', 'thermal engineering', 'fluid mechanics',
                'mechatronics', 'design engineering', 'tribology', 'dynamics'],

        '2.4': ['chemical engineering', 'process engineering', 'petrochemical',
                'refining', 'industrial chemistry', 'reaction engineering'],

        '2.5': ['materials science', 'materials engineering', 'metallurgy', 'ceramics',
                'composites', 'biomaterials', 'polymers', 'materials characterization',
                'surface engineering', 'smart materials'],

        '2.6': ['biomedical engineering', 'medical engineering', 'medical devices',
                'prosthetics', 'tissue engineering', 'rehabilitation engineering',
                'clinical engineering', 'medical imaging engineering'],

        '2.7': ['environmental engineering', 'water treatment', 'waste management',
                'pollution control', 'sanitation', 'air quality', 'environmental technology'],

        '2.8': ['environmental biotechnology', 'bioremediation', 'green technology',
                'sustainable biotechnology', 'environmental bioprocessing'],

        '2.9': ['industrial biotechnology', 'bioprocessing', 'fermentation',
                'enzyme technology', 'biomanufacturing', 'white biotechnology'],

        '2.10': ['nanotechnology', 'nano', 'nanoscience', 'nanomaterials',
                 'nanoelectronics', 'nanomedicine', 'nanoengineering', 'nanofabrication'],

        '2.11': ['engineering', 'applied science', 'technology', 'industrial engineering',
                 'systems engineering', 'engineering science'],

        # Medical and Health Sciences
        '3.1': ['basic medicine', 'anatomy', 'physiology', 'pathology', 'immunology',
                'pharmacology', 'toxicology', 'medical science', 'biomedical science',
                'medical physiology', 'medical biochemistry', 'medical microbiology'],

        '3.2': ['clinical medicine', 'medicine', 'surgery', 'oncology', 'cardiology',
                'neurology', 'pediatrics', 'psychiatry', 'radiology', 'anesthesiology',
                'emergency medicine', 'internal medicine', 'dermatology', 'ophthalmology',
                'obstetrics', 'gynecology', 'urology', 'orthopedics', 'gastroenterology',
                'endocrinology', 'rheumatology', 'infectious diseases', 'clinical'],

        '3.3': ['health sciences', 'public health', 'epidemiology', 'nursing',
                'nutrition', 'occupational health', 'health policy', 'health management',
                'health education', 'preventive medicine', 'health care', 'health services',
                'primary care', 'community health', 'global health'],

        '3.4': ['medical biotechnology', 'gene therapy', 'regenerative medicine',
                'pharmaceutical biotechnology', 'diagnostic biotechnology', 'biopharmaceuticals'],

        '3.5': ['medical sciences', 'health research', 'medical research', 'clinical research'],

        # Agricultural Sciences
        '4.1': ['agriculture', 'agricultural', 'agronomy', 'crop science', 'horticulture',
                'forestry', 'fisheries', 'aquaculture', 'agroforestry', 'soil science',
                'plant science', 'precision agriculture', 'sustainable agriculture'],

        '4.2': ['animal science', 'dairy science', 'livestock', 'animal husbandry',
                'poultry science', 'animal nutrition', 'animal breeding', 'zootechnics'],

        '4.3': ['veterinary', 'veterinary medicine', 'animal health', 'veterinary science',
                'veterinary pathology', 'veterinary surgery'],

        '4.4': ['agricultural biotechnology', 'plant biotechnology', 'genetic engineering',
                'crop biotechnology', 'agricultural genetics', 'bioagriculture'],

        '4.5': ['food science', 'food technology', 'agricultural engineering',
                'rural development', 'agricultural economics'],

        # Social Sciences
        '5.1': ['psychology', 'psychological', 'cognitive science', 'behavioral science',
                'neuropsychology', 'developmental psychology', 'social psychology',
                'clinical psychology', 'educational psychology', 'psychotherapy'],

        '5.2': ['economics', 'business', 'finance', 'management', 'accounting',
                'marketing', 'entrepreneurship', 'econometrics', 'macroeconomics',
                'microeconomics', 'business administration', 'operations research',
                'organizational behavior', 'strategic management', 'human resource'],

        '5.3': ['education', 'educational', 'pedagogy', 'teaching', 'learning',
                'curriculum', 'instructional', 'higher education', 'educational technology',
                'educational psychology', 'educational research'],

        '5.4': ['sociology', 'social', 'anthropology', 'demography', 'social work',
                'social policy', 'urban studies', 'family studies', 'criminology',
                'social theory', 'cultural studies'],

        '5.5': ['law', 'legal', 'jurisprudence', 'international law', 'criminal law',
                'civil law', 'constitutional law', 'legal studies', 'legislation'],

        '5.6': ['political science', 'politics', 'government', 'public administration',
                'international relations', 'public policy', 'political theory',
                'comparative politics', 'governance'],

        '5.7': ['geography', 'human geography', 'economic geography', 'urban geography',
                'regional studies', 'spatial analysis', 'GIS', 'cartography'],

        '5.8': ['media', 'communication', 'journalism', 'mass communication',
                'information science', 'library science', 'media studies',
                'digital media', 'broadcasting', 'public relations'],

        '5.9': ['social sciences', 'interdisciplinary social science', 'area studies',
                'development studies', 'gender studies', 'environmental social science'],

        # Humanities
        '6.1': ['history', 'historical', 'archaeology', 'classical studies',
                'ancient history', 'medieval history', 'modern history', 'historiography',
                'paleography', 'numismatics', 'heritage studies'],

        '6.2': ['literature', 'literary', 'language', 'linguistics', 'philology',
                'comparative literature', 'english literature', 'translation studies',
                'applied linguistics', 'sociolinguistics', 'language studies'],

        '6.3': ['philosophy', 'ethics', 'religion', 'theology', 'religious studies',
                'metaphysics', 'epistemology', 'moral philosophy', 'logic',
                'philosophy of science', 'bioethics'],

        '6.4': ['arts', 'art history', 'music', 'theater', 'film studies', 'dance',
                'visual arts', 'performing arts', 'musicology', 'fine arts',
                'cultural heritage', 'aesthetics', 'art theory'],

        '6.5': ['humanities', 'interdisciplinary humanities', 'cultural studies',
                'digital humanities', 'liberal arts']
    }

    def __init__(self):
        """Initialize the FieldClassifier with pre-compiled patterns."""
        self.keyword_patterns = self._compile_keyword_patterns()
        logger.info("FieldClassifier initialized with OECD classification schema")

    def _compile_keyword_patterns(self) -> Dict[str, List[re.Pattern]]:
        """
        Compile regex patterns for efficient keyword matching.

        Returns:
            Dictionary mapping field codes to compiled regex patterns
        """
        patterns = {}
        for field_code, keywords in self.FIELD_KEYWORDS.items():
            patterns[field_code] = [
                re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                for keyword in keywords
            ]
        return patterns

    def classify_by_name(self, journal_name: str,
                        top_n: int = 3,
                        min_confidence: float = 0.1) -> List[Dict[str, any]]:
        """
        Classify journal based on keywords in journal name.

        Args:
            journal_name: Name/title of the journal
            top_n: Maximum number of field classifications to return
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of classification results, each containing:
            - field_code: OECD field code (e.g., '1.2')
            - field_name: Full name of the field
            - major_field_code: Major field code (e.g., '1')
            - major_field_name: Major field name
            - confidence: Confidence score (0-1)
            - matched_keywords: List of keywords that matched

        Example:
            >>> classifier = FieldClassifier()
            >>> results = classifier.classify_by_name("Journal of Machine Learning Research")
            >>> results[0]['field_name']
            'Computer and information sciences'
        """
        if not journal_name or not isinstance(journal_name, str):
            logger.warning("Invalid journal name provided")
            return []

        journal_name = journal_name.lower().strip()
        field_scores = {}

        # Count keyword matches for each field
        for field_code, patterns in self.keyword_patterns.items():
            matched_keywords = []
            match_count = 0

            for pattern in patterns:
                matches = pattern.findall(journal_name)
                if matches:
                    match_count += len(matches)
                    matched_keywords.extend(matches)

            if match_count > 0:
                # Calculate confidence based on:
                # 1. Number of matches
                # 2. Length of journal name (normalize)
                # 3. Uniqueness of keywords
                word_count = len(journal_name.split())
                confidence = min(1.0, (match_count / max(word_count, 1)) * 1.5)

                field_scores[field_code] = {
                    'confidence': confidence,
                    'matched_keywords': list(set(matched_keywords))
                }

        # Sort by confidence and get top N
        sorted_fields = sorted(
            field_scores.items(),
            key=lambda x: x[1]['confidence'],
            reverse=True
        )[:top_n]

        # Format results
        results = []
        for field_code, score_data in sorted_fields:
            if score_data['confidence'] >= min_confidence:
                major_code = field_code.split('.')[0]
                results.append({
                    'field_code': field_code,
                    'field_name': self.SUB_FIELDS[field_code],
                    'major_field_code': major_code,
                    'major_field_name': self.MAJOR_FIELDS[major_code],
                    'confidence': round(score_data['confidence'], 3),
                    'matched_keywords': score_data['matched_keywords']
                })

        logger.info(f"Classified '{journal_name}' into {len(results)} fields")
        return results

    def classify_by_topics(self, topics_list: List[str],
                          top_n: int = 3,
                          min_confidence: float = 0.1) -> List[Dict[str, any]]:
        """
        Classify journal based on OpenAlex topics or subject keywords.

        Args:
            topics_list: List of topic strings or subject keywords
            top_n: Maximum number of field classifications to return
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of classification results with field codes and confidence scores

        Example:
            >>> topics = ["Machine Learning", "Neural Networks", "AI"]
            >>> results = classifier.classify_by_topics(topics)
        """
        if not topics_list or not isinstance(topics_list, list):
            logger.warning("Invalid topics list provided")
            return []

        # Combine all topics into a single searchable text
        combined_text = " ".join(str(topic) for topic in topics_list if topic)

        # Use the same classification logic as name-based
        return self.classify_by_name(combined_text, top_n=top_n, min_confidence=min_confidence)

    def classify_by_issn(self, issn: str,
                        issn_database: Dict[str, List[str]]) -> List[Dict[str, any]]:
        """
        Look up field classification from existing ISSN→field mapping database.

        Args:
            issn: ISSN identifier (with or without hyphen)
            issn_database: Dictionary mapping ISSNs to field codes
                          Format: {'ISSN': ['field_code1', 'field_code2', ...]}

        Returns:
            List of classification results with confidence 1.0 (database lookup)

        Example:
            >>> issn_db = {'0028-0836': ['1.3', '1.6']}  # Nature journal
            >>> results = classifier.classify_by_issn('0028-0836', issn_db)
        """
        if not issn or not isinstance(issn, str):
            logger.warning("Invalid ISSN provided")
            return []

        if not issn_database or not isinstance(issn_database, dict):
            logger.warning("Invalid ISSN database provided")
            return []

        # Normalize ISSN (remove spaces, convert to uppercase)
        normalized_issn = issn.replace(' ', '').replace('-', '').upper()

        # Try multiple ISSN formats
        issn_variants = [
            issn,
            normalized_issn,
            f"{normalized_issn[:4]}-{normalized_issn[4:]}" if len(normalized_issn) == 8 else issn
        ]

        field_codes = []
        for variant in issn_variants:
            if variant in issn_database:
                field_codes = issn_database[variant]
                break

        if not field_codes:
            logger.info(f"No field mapping found for ISSN: {issn}")
            return []

        # Format results with confidence 1.0 (database lookup)
        results = []
        for field_code in field_codes:
            if field_code in self.SUB_FIELDS:
                major_code = field_code.split('.')[0]
                results.append({
                    'field_code': field_code,
                    'field_name': self.SUB_FIELDS[field_code],
                    'major_field_code': major_code,
                    'major_field_name': self.MAJOR_FIELDS[major_code],
                    'confidence': 1.0,
                    'source': 'issn_database'
                })

        logger.info(f"Found {len(results)} field(s) for ISSN: {issn}")
        return results

    def get_field_hierarchy(self, field_code: str) -> Optional[Dict[str, any]]:
        """
        Get parent/child relationships for a field code.

        Args:
            field_code: OECD field code (e.g., '1.2' or '1')

        Returns:
            Dictionary containing:
            - field_code: The input field code
            - field_name: Name of the field
            - level: 'major' or 'sub'
            - parent: Parent field info (if sub-field)
            - children: List of child fields (if major field)
            - siblings: List of sibling fields (if sub-field)

        Example:
            >>> hierarchy = classifier.get_field_hierarchy('1.2')
            >>> hierarchy['parent']['field_name']
            'Natural Sciences'
        """
        if not field_code or not isinstance(field_code, str):
            logger.warning("Invalid field code provided")
            return None

        field_code = field_code.strip()

        # Check if it's a major field
        if field_code in self.MAJOR_FIELDS:
            # Get all sub-fields for this major field
            children = [
                {
                    'field_code': sub_code,
                    'field_name': sub_name
                }
                for sub_code, sub_name in self.SUB_FIELDS.items()
                if sub_code.startswith(field_code + '.')
            ]

            return {
                'field_code': field_code,
                'field_name': self.MAJOR_FIELDS[field_code],
                'level': 'major',
                'parent': None,
                'children': children,
                'siblings': []
            }

        # Check if it's a sub-field
        elif field_code in self.SUB_FIELDS:
            major_code = field_code.split('.')[0]

            # Get sibling fields
            siblings = [
                {
                    'field_code': sub_code,
                    'field_name': sub_name
                }
                for sub_code, sub_name in self.SUB_FIELDS.items()
                if sub_code.startswith(major_code + '.') and sub_code != field_code
            ]

            return {
                'field_code': field_code,
                'field_name': self.SUB_FIELDS[field_code],
                'level': 'sub',
                'parent': {
                    'field_code': major_code,
                    'field_name': self.MAJOR_FIELDS[major_code]
                },
                'children': [],
                'siblings': siblings
            }

        else:
            logger.warning(f"Field code '{field_code}' not found in OECD schema")
            return None

    def classify_multi_method(self, journal_name: str = None,
                             topics_list: List[str] = None,
                             issn: str = None,
                             issn_database: Dict[str, List[str]] = None,
                             top_n: int = 3) -> Dict[str, any]:
        """
        Combine multiple classification methods for best results.

        Args:
            journal_name: Journal name/title
            topics_list: List of topics or subject keywords
            issn: ISSN identifier
            issn_database: ISSN→field mapping database
            top_n: Maximum results to return

        Returns:
            Dictionary containing:
            - classifications: Combined and ranked field classifications
            - methods_used: List of methods that contributed
            - aggregated_confidence: Weighted confidence scores

        Example:
            >>> results = classifier.classify_multi_method(
            ...     journal_name="Nature",
            ...     topics_list=["biology", "chemistry"],
            ...     issn="0028-0836"
            ... )
        """
        all_classifications = {}
        methods_used = []

        # Method 1: ISSN lookup (highest priority)
        if issn and issn_database:
            issn_results = self.classify_by_issn(issn, issn_database)
            if issn_results:
                methods_used.append('issn_lookup')
                for result in issn_results:
                    field_code = result['field_code']
                    all_classifications[field_code] = {
                        'result': result,
                        'score': result['confidence'] * 1.0  # Weight: 1.0
                    }

        # Method 2: Topic classification (medium priority)
        if topics_list:
            topic_results = self.classify_by_topics(topics_list, top_n=top_n)
            if topic_results:
                methods_used.append('topic_classification')
                for result in topic_results:
                    field_code = result['field_code']
                    weighted_score = result['confidence'] * 0.7  # Weight: 0.7

                    if field_code in all_classifications:
                        # Combine scores
                        all_classifications[field_code]['score'] += weighted_score
                    else:
                        all_classifications[field_code] = {
                            'result': result,
                            'score': weighted_score
                        }

        # Method 3: Name classification (lower priority)
        if journal_name:
            name_results = self.classify_by_name(journal_name, top_n=top_n)
            if name_results:
                methods_used.append('name_classification')
                for result in name_results:
                    field_code = result['field_code']
                    weighted_score = result['confidence'] * 0.5  # Weight: 0.5

                    if field_code in all_classifications:
                        # Combine scores
                        all_classifications[field_code]['score'] += weighted_score
                    else:
                        all_classifications[field_code] = {
                            'result': result,
                            'score': weighted_score
                        }

        # Normalize scores and sort
        if all_classifications:
            max_score = max(item['score'] for item in all_classifications.values())

            for field_code in all_classifications:
                all_classifications[field_code]['normalized_confidence'] = round(
                    all_classifications[field_code]['score'] / max_score, 3
                )

            # Sort by score and get top N
            sorted_classifications = sorted(
                all_classifications.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )[:top_n]

            # Format final results
            final_results = []
            for field_code, data in sorted_classifications:
                result = data['result'].copy()
                result['aggregated_confidence'] = data['normalized_confidence']
                final_results.append(result)

            return {
                'classifications': final_results,
                'methods_used': methods_used,
                'total_methods': len(methods_used)
            }

        else:
            logger.warning("No classifications found with any method")
            return {
                'classifications': [],
                'methods_used': [],
                'total_methods': 0
            }

    def validate_field_code(self, field_code: str) -> bool:
        """
        Validate if a field code exists in the OECD schema.

        Args:
            field_code: Field code to validate

        Returns:
            True if valid, False otherwise
        """
        return (field_code in self.MAJOR_FIELDS or
                field_code in self.SUB_FIELDS)

    def get_all_fields(self, level: str = 'all') -> Dict[str, str]:
        """
        Get all field codes and names.

        Args:
            level: 'major', 'sub', or 'all'

        Returns:
            Dictionary of field codes and names
        """
        if level == 'major':
            return self.MAJOR_FIELDS.copy()
        elif level == 'sub':
            return self.SUB_FIELDS.copy()
        else:
            return {**self.MAJOR_FIELDS, **self.SUB_FIELDS}

    def search_fields(self, query: str) -> List[Dict[str, str]]:
        """
        Search for fields by name or keyword.

        Args:
            query: Search query string

        Returns:
            List of matching fields with codes and names
        """
        query_lower = query.lower().strip()
        results = []

        # Search in field names
        for code, name in {**self.MAJOR_FIELDS, **self.SUB_FIELDS}.items():
            if query_lower in name.lower():
                level = 'major' if code in self.MAJOR_FIELDS else 'sub'
                results.append({
                    'field_code': code,
                    'field_name': name,
                    'level': level
                })

        return results


# Convenience functions for quick usage

def classify_journal(journal_name: str, top_n: int = 3) -> List[Dict[str, any]]:
    """
    Quick classification by journal name.

    Args:
        journal_name: Name of the journal
        top_n: Number of top results to return

    Returns:
        List of classification results
    """
    classifier = FieldClassifier()
    return classifier.classify_by_name(journal_name, top_n=top_n)


def get_field_info(field_code: str) -> Optional[Dict[str, any]]:
    """
    Quick field information lookup.

    Args:
        field_code: OECD field code

    Returns:
        Field hierarchy information
    """
    classifier = FieldClassifier()
    return classifier.get_field_hierarchy(field_code)


# Example usage and testing
if __name__ == "__main__":
    # Initialize classifier
    classifier = FieldClassifier()

    print("=" * 80)
    print("OECD Field Classifier - Example Usage")
    print("=" * 80)

    # Example 1: Classify by journal name
    print("\n1. Classification by Journal Name:")
    print("-" * 80)
    journals = [
        "Nature",
        "Journal of Machine Learning Research",
        "The Lancet",
        "IEEE Transactions on Neural Networks",
        "Agricultural Economics"
    ]

    for journal in journals:
        results = classifier.classify_by_name(journal, top_n=2)
        print(f"\nJournal: {journal}")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['field_name']} ({result['field_code']})")
            print(f"     Confidence: {result['confidence']:.2%}")
            print(f"     Keywords: {', '.join(result['matched_keywords'][:3])}")

    # Example 2: Classify by topics
    print("\n\n2. Classification by Topics:")
    print("-" * 80)
    topics = ["machine learning", "neural networks", "artificial intelligence"]
    results = classifier.classify_by_topics(topics, top_n=3)
    print(f"Topics: {', '.join(topics)}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['field_name']} ({result['field_code']})")
        print(f"     Confidence: {result['confidence']:.2%}")

    # Example 3: Field hierarchy
    print("\n\n3. Field Hierarchy:")
    print("-" * 80)
    hierarchy = classifier.get_field_hierarchy('1.2')
    if hierarchy:
        print(f"Field: {hierarchy['field_name']} ({hierarchy['field_code']})")
        print(f"Level: {hierarchy['level']}")
        print(f"Parent: {hierarchy['parent']['field_name']}")
        print(f"Siblings: {len(hierarchy['siblings'])} sub-fields")

    # Example 4: Multi-method classification
    print("\n\n4. Multi-Method Classification:")
    print("-" * 80)
    results = classifier.classify_multi_method(
        journal_name="Nature Biotechnology",
        topics_list=["biotechnology", "genetics", "molecular biology"],
        top_n=3
    )
    print(f"Methods used: {', '.join(results['methods_used'])}")
    for i, result in enumerate(results['classifications'], 1):
        print(f"  {i}. {result['field_name']} ({result['field_code']})")
        print(f"     Aggregated Confidence: {result['aggregated_confidence']:.2%}")

    # Example 5: Search fields
    print("\n\n5. Field Search:")
    print("-" * 80)
    search_results = classifier.search_fields("computer")
    print(f"Search query: 'computer'")
    for result in search_results:
        print(f"  - {result['field_name']} ({result['field_code']}) [{result['level']}]")

    print("\n" + "=" * 80)
    print("Total OECD Fields:")
    print(f"  Major Fields: {len(classifier.MAJOR_FIELDS)}")
    print(f"  Sub-Fields: {len(classifier.SUB_FIELDS)}")
    print("=" * 80)
