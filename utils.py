import re
from typing import Optional


def text_to_minutes(text: str) -> Optional[int]:
    patterns = [
        r'(\d+)\s+ώρες\s+και\s+(\d+)\'',
        r'(\d+)\s+ώρα\s+και\s+(\d+)\'',
        r'(\d+)\'',
        r'(\d+)\s+ώρα',
        r'(\d+)\s+ώρες',
    ]

    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                hours, minutes = map(int, groups)
            elif len(groups) == 1:
                hours = 0
                minutes = int(groups[0])
            else:
                return None

            total_minutes = hours * 60 + minutes
            return total_minutes

    return None
