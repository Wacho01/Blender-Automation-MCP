from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OperationType(str, Enum):
    READ = "read"
    MODIFY = "modify"
    FILESYSTEM = "filesystem"
    EXECUTION = "execution"
    ADMINISTRATIVE = "administrative"


class SecurityLevel(str, Enum):
    STANDARD = "standard"
    RESTRICTED = "restricted"
    PRIVILEGED = "privileged"


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    id: str
    category: str
    description: str
    operation_type: OperationType
    security_level: SecurityLevel = SecurityLevel.STANDARD
    undo_supported: bool = False
    async_supported: bool = False
    enabled: bool = True
    deprecated: bool = False
    minimum_blender_version: str = "3.6"
    maximum_blender_version: str | None = None
    input_schema: str | None = None
    result_schema: str | None = None

    def __post_init__(self) -> None:
        capability_id = self.id.strip()
        category = self.category.strip()
        description = self.description.strip()

        if not capability_id:
            raise ValueError("Capability id cannot be empty.")

        if "." not in capability_id:
            raise ValueError(
                "Capability id must use the 'category.operation' format."
            )

        if not category:
            raise ValueError("Capability category cannot be empty.")

        if not description:
            raise ValueError("Capability description cannot be empty.")

        object.__setattr__(self, "id", capability_id)
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "description", description)
