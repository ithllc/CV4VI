import re

def extract_and_normalize_location(query: str) -> str | None:
    """
    Extracts and normalizes a location from a user query.
    Example: "I'm at 1st Avenue and 110th Street, can I cross?" -> "1 Ave @ 110 St"
    """
    # Regex to find street intersections, including variations like "I'm at..."
    # First try to find a pattern with number + street type
    match = re.search(r"""
        (?P<street1>\d+(?:st|nd|rd|th)?\s+(?:avenue|ave|street|st|road|rd|boulevard|blvd|drive|dr|place|pl|court|ct))
        \s+(?:and|&|@)\s+
        (?P<street2>\d+(?:st|nd|rd|th)?\s+(?:avenue|ave|street|st|road|rd|boulevard|blvd|drive|dr|place|pl|court|ct))
    """, query, re.IGNORECASE | re.VERBOSE)
    
    # If no match, try a broader pattern but with better boundaries
    if not match:
        match = re.search(r"""
            (?P<street1>(?:\d+(?:st|nd|rd|th)?\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)*\s+(?:avenue|ave|street|st|road|rd|boulevard|blvd|drive|dr|place|pl|court|ct))
            \s+(?:and|&|@)\s+
            (?P<street2>(?:\d+(?:st|nd|rd|th)?\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)*\s+(?:avenue|ave|street|st|road|rd|boulevard|blvd|drive|dr|place|pl|court|ct))
        """, query, re.IGNORECASE | re.VERBOSE)

    if not match:
        return None

    def normalize_street(s: str) -> str:
        s = s.lower().strip()
        
        # Remove extra whitespace
        s = ' '.join(s.split())

        # Convert written numbers to digits
        num_map = {
            'first': '1', 'second': '2', 'third': '3', 'fourth': '4', 'fifth': '5',
            'sixth': '6', 'seventh': '7', 'eighth': '8', 'ninth': '9', 'tenth': '10'
        }
        for word, digit in num_map.items():
            s = s.replace(word, digit)

        # Remove ordinal suffixes (st, nd, rd, th) but keep the number
        s = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', s)

        # Abbreviate and capitalize street types
        type_map = {
            'avenue': 'Ave', 'ave': 'Ave',
            'street': 'St', 'st': 'St',
            'road': 'Rd', 'rd': 'Rd',
            'boulevard': 'Blvd', 'blvd': 'Blvd',
            'drive': 'Dr', 'dr': 'Dr',
            'place': 'Pl', 'pl': 'Pl',
            'court': 'Ct', 'ct': 'Ct'
        }

        parts = s.split()
        name_parts = []
        type_part = ""

        for part in parts:
            if part in type_map:
                type_part = type_map[part]
            else:
                # Capitalize name parts, but handle numbers correctly
                name_parts.append(part.title() if not part.isdigit() else part)
        
        # Join name parts and add the type
        full_name = " ".join(name_parts)
        if type_part:
            full_name += f" {type_part}"
        
        return full_name

    street1 = normalize_street(match.group('street1'))
    street2 = normalize_street(match.group('street2'))

    return f"{street1} @ {street2}"
