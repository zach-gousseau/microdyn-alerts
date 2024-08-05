import re

class KeywordSearch:
    def __init__(self):
        # keywords and their variations
        self.keywords = {
            # Overarching
            "Prospective Payment Systems": r"\bProspective\s*Payment\s*Systems\b|\bPPS\b",
            "Prospective Payment System": r"\bProspective\s*Payment\s*System\b|\bPPS\b",

            # Products
            "Inpatient Prospective Payment System": r"\bInpatient\s*Prospective\s*Payment\s*System\b|\bIPPS\b",
            "Outpatient Prospective Payment System": r"\bOutpatient\s*Prospective\s*Payment\s*System\b|\bOPPS\b",
            "Ambulatory Payment Classification": r"\bAmbulatory\s*Payment\s*Classification\b|\bAPC\b",
            "Ambulatory Surgical Center": r"\bAmbulatory\s*Surgical\s*Center\b|\bASC\b",
            "Home Health": r"\bHome\s*Health\b|\bHH\b",
            "PDGM": r"\bPDGM\b",
            "End Stage Renal Disease": r"\bEnd\s*Stage\s*Renal\s*Disease\b|\bESRD\b",
            "Hospice": r"\bHospice\b",
            "FQHC": r"\bFQHC\b",
            "Long-Term Care Hospital": r"\bLong-Term\s*Care\s*Hospital\b|\bLTCH\b|\bLTC\b",
            "Skilled Nursing Facility": r"\bSkilled\s*Nursing\s*Facility\b|\bSNF\b",
            "Inpatient Psychiatric Facility": r"\bInpatient\s*Psychiatric\s*Facility\b|\bPsych\b",
            "Inpatient Rehabilitation Facility": r"\bInpatient\s*Rehabilitation\s*Facility\b|\bIRF\b",
            "Critical Access Hospital": r"\bCritical\s*Access\s*Hospital\b",

            # Additional keywords
            "DRG": r"\bDRG\b",
            "MS-DRG": r"\bMS-DRG\b",
            "Pricer": r"\bPricer\b",
            "Grouper": r"\bGrouper\b",
            "Web Pricer": r"\bWeb\s*Pricer\b",
            "Provider data files": r"\bProvider\s*data\s*files\b",
            "HCPCS": r"\bHCPCS\b",
            "HIPPS": r"\bHIPPS\b"
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