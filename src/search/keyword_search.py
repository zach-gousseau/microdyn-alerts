import re

class KeywordSearch:
    def __init__(self):
        
        # keywords and their variations
        self.keywords = {
            # Overarching
            "Prospective Payment System": r"\bProspective[-\s]*Payment[-\s]*Systems?\b|\bPPS\b",

            # Products
            "Inpatient Prospective Payment System": r"\bInpatient[-\s]*Prospective[-\s]*Payment[-\s]*Systems?\b|\bIPPS\b",
            "Outpatient Prospective Payment System": r"\bOutpatient[-\s]*Prospective[-\s]*Payment[-\s]*Systems?\b|\bOPPS\b",
            "Ambulatory Payment Classification": r"\bAmbulatory\s*Payment\s*Classification\b|\bAPC\b",
            "Ambulatory Surgical Center": r"\bAmbulatory\s*Surgical\s*Center\b|\bASC\b|\basc\b",
            "Home Health": r"\bHome\s*Health\b|\bHH\b|\bHHs\b",
            "PDGM": r"\b(PDGM|Patient[-\s]*Driven\s*Grouping(s?)\s*Model)\b",
            "End Stage Renal Disease": r"\bEnd\s*Stage\s*Renal\s*Disease\b|\bESRD\b",
            "Hospice": r"\bHospice\b",
            "FQHC": r"\b(FQHC|fqhc|Federally[-\s]*Qualified\s*Health\s*Centers?)\b",
            "Long-Term Care Hospital": r"\bLong[-\s]*Term[-\s]*Care[-\s]*Hospitals?\b|\bLTCH\b|\bLTC\b",
            "Skilled Nursing Facility": r"\bSkilled\s*Nursing\s*Facilities?\b|\bSNF\b",
            "Inpatient Psychiatric Facility": r"\bInpatient\s*Psychiatric\s*Facilities?\b|\bIPF\b|\bPsych\b",
            "Inpatient Rehabilitation Facility": r"\bInpatient\s*Rehabilitation\s*Facilities?\b|\bIRF\b",
            "Critical Access Hospital": r"\bCritical\s*Access\s*Hospitals?\b",

            # Additional keywords
            "DRG": r"\b(DRG|drg|Diagnosis[-\s]*Related\s*Group)\b",
            "MS-DRG": r"\b(MS-DRG|Medicare\s*Severity\s*Diagnosis[-\s]*Related\s*Group)\b",
            "Pricer": r"\bPricer\b",
            "Grouper": r"\bGrouper\b",
            "Web Pricer": r"\bWeb\s*Pricer\b",
            "Provider data files": r"\b[Pp]rovider\s*[Dd]ata\s*[Ff]ile[s]?\b",
            "HCPCS": r"\b(HCPCS|hcpcs|Healthcare\s*Common\s*Procedure\s*Coding\s*System)\b",
            "HIPPS": r"\b(HIPPS|hipps|Health\s*Insurance\s*Prospective\s*Payment\s*System)\b",
        }
        
    def find_keywords_in_paragraphs(self, paragraphs):
        keyword_paragraphs = []
        matched_keywords = set()

        for paragraph in paragraphs:
            for keyword, pattern in self.keywords.items():
                if re.search(pattern, paragraph, re.IGNORECASE):
                    keyword_paragraphs.append(paragraph)
                    matched_keywords.add(keyword)

        if len(keyword_paragraphs) == 0:
            return None
        else:
            return keyword_paragraphs, list(matched_keywords)