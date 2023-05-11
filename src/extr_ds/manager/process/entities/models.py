from typing import Dict, List
from dataclasses import dataclass, field


@dataclass()
class Annotations:
    text: List[str] = field(default_factory=lambda: [])
    html: List[str] = field(default_factory=lambda: [])
    text_by_label: Dict[str, List[str]] = field( default_factory=lambda: {})
