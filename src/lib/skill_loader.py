import yaml
from pathlib import Path
import re
import logging

class SkillLoader:
    """Validates and loads SKILL.md metadata for agent capabilities."""
    
    @staticmethod
    def load_skill(skill_dir: str | Path) -> dict:
        """
        Loads metadata from SKILL.md in the given directory.
        Expects a front-matter block with YAML content.
        """
        skill_file = Path(skill_dir) / "SKILL.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"Skill definition not found: {skill_file}")
            
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match front-matter (e.g., between triple dashes)
        match = re.search(r'^---\s*
(.*?)
---\s*
', content, re.DOTALL)
        if not match:
            raise ValueError(f"Front-matter missing in {skill_file}")
            
        metadata = yaml.safe_load(match.group(1))
        return metadata

    @classmethod
    def validate_skill(cls, skill_dir: str | Path) -> bool:
        """Validates that a skill has required fields."""
        metadata = cls.load_skill(skill_dir)
        required = ["name", "description", "version"]
        for field in required:
            if field not in metadata:
                raise KeyError(f"Missing required skill field: {field}")
        return True

if __name__ == "__main__":
    # Test would go here once a SKILL.md exists
    pass
