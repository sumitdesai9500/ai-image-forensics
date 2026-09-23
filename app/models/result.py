from dataclasses import dataclass, field
from typing import Any

@dataclass
class ForensicEvidence:
    file: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    container: dict[str, Any] = field(default_factory=dict)
    pixel: dict[str, Any] = field(default_factory=dict)
    transformations: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__
