from dataclasses import dataclass, field
from enum import Enum
from typing import List

class BuildType(Enum):
    HTML=0
    PDF=1

@dataclass
class SrcMeta:
    node_name: str
    path: str
    build_type: BuildType = BuildType.HTML
    
    def __repr__(self) -> str:
        return f"node_name: {self.node_name}\n path: {self.path} -> {self.build_type}"

# Page Wise processing types
@dataclass
class SiteMeta:
    cssfile: str

@dataclass
class PageMeta:
    tags: List[str]
    description: str | None
    convert_to: BuildType
    

