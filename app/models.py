
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Stats(BaseModel):
    hp: int = 0
    max_hp: int = 0
    atk: int = 0
    def_: int = Field(0, alias="def")
    spd: int = 0
    mana: int = 0

class EffectAction(BaseModel):
    type: str
    amount: Optional[int] = 0
    multiplier: Optional[str] = None
    damage_type: Optional[str] = "Physical"
    effect_id: Optional[str] = None
    duration: Optional[int] = 0
    chance: float = 1.0

class SkillConfig(BaseModel):
    name: str
    costs: Dict[str, Any]
    effekte: List[EffectAction]

class StatusEffectConfig(BaseModel):
    name: str
    tick_effect: Optional[EffectAction] = None
    modifier: Optional[Dict[str, Any]] = None

class ItemConfig(BaseModel):
    name: str
    type: str
    icon_id: str
    slot: Optional[str] = None
    stats_bonus: Optional[Dict[str, float]] = None
    value_gold: int
    max_stack: int = 1

class OpponentData(BaseModel):
    name: str = "Unknown"
    stats: Stats = Stats()
    faction: str = "Neutral"
    skills: List[str] = []
    ai_policy: str = "Basic"
    xp: int = 0
    loot_table_id: Optional[str] = None
