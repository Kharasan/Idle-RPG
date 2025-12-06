
import json5
import os
from typing import List, Any
from .models import ItemConfig, OpponentData, Stats

class ConfigLoaderService:
    def __init__(self):
        self.items = {}

    def load_items(self, filepath='config/items.json5'):
        if not os.path.exists(filepath): return
        with open(filepath, 'r') as f:
            data = json5.load(f)
        for k, v in data.items():
            self.items[k] = ItemConfig(**v)
            
    def get_item(self, item_id: str):
        return self.items.get(item_id)

class AIPolicyService:
    def decide_action(self, policy_id: str, me: Any, enemies: List[Any], allies: List[Any]) -> str:
        # Einfache Logik für den Moment
        if policy_id == "Healer":
            injured = [a for a in allies if a.stats.hp < (a.stats.max_hp * 0.5)]
            if injured: return "heal"
        
        # Standard: Aggressiv
        return "attack"

class OpponentFactory:
    def __init__(self):
        self.archetypes = {}
        self.opponents_config = {}
        self._load_data()

    def _load_data(self):
        # Basis laden
        for fpath in ['config/archetypes/base.json5', 'config/archetypes/roles.json5']:
            if os.path.exists(fpath):
                with open(fpath) as f: self.archetypes.update(json5.load(f))
        
        if os.path.exists('config/opponents.json5'):
            with open('config/opponents.json5') as f: self.opponents_config = json5.load(f)

    def _apply_stat_modifier(self, current_val: int, modifier: Any) -> int:
        if isinstance(modifier, str):
            if modifier.startswith("+"): return current_val + int(modifier[1:])
            elif modifier.startswith("-"): return current_val - int(modifier[1:])
        return int(modifier)

    def create_opponent(self, opponent_id: str) -> OpponentData:
        if opponent_id not in self.opponents_config: return None
        config = self.opponents_config[opponent_id]
        
        final_data = {
            "stats": {"hp": 0, "max_hp": 0, "atk": 0, "def": 0, "spd": 0, "mana": 0},
            "skills": [],
            "faction": "Neutral",
            "ai_policy": "Basic"
        }

        # Archetypen anwenden
        for arch_id in config.get("archetypes", []):
            arch_data = self.archetypes.get(arch_id, {})
            # Stats
            if "stats" in arch_data:
                for stat, val in arch_data["stats"].items():
                    # Mapping für 'def' weil es in Python reserviert ist
                    key = "def" if stat == "def" else stat 
                    # Für unsere interne Logik nutzen wir def_ im Modell, aber JSON hat def
                    target_key = "def" # JSON key
                    
                    # Hier vereinfacht: Wir schreiben in ein Dict, das später ins Modell geparst wird
                    current = final_data["stats"].get(stat, 0)
                    final_data["stats"][stat] = self._apply_stat_modifier(current, val)
                    
            # Skills
            if "skills" in arch_data:
                for s in arch_data["skills"]:
                    if s not in final_data["skills"]: final_data["skills"].append(s)
            
            # Meta
            for f in ["faction", "ai_policy"]:
                if f in arch_data: final_data[f] = arch_data[f]

        # Overrides
        overrides = config.get("overrides", {})
        if "stats" in overrides:
            for stat, val in overrides["stats"].items():
                current = final_data["stats"].get(stat, 0)
                final_data["stats"][stat] = self._apply_stat_modifier(current, val)
        
        if "skills" in overrides:
            for s in overrides["skills"]:
                if s not in final_data["skills"]: final_data["skills"].append(s)
                
        if "ai_policy" in overrides: final_data["ai_policy"] = overrides["ai_policy"]

        final_data["name"] = config.get("name", "Unknown")
        final_data["xp"] = config.get("xp", 0)
        
        # Max HP setzen (ist am Anfang gleich HP)
        if final_data["stats"]["max_hp"] == 0:
             final_data["stats"]["max_hp"] = final_data["stats"]["hp"]

        # Rename def -> def_ für Pydantic
        if "def" in final_data["stats"]:
            final_data["stats"]["def_"] = final_data["stats"]["def"]
            del final_data["stats"]["def"]

        return OpponentData(**final_data)
