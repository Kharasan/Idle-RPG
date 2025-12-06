
from app.services import OpponentFactory, ConfigLoaderService, AIPolicyService
from app.engine import BattleEngine, EffectEngine

class HeroMock:
    def __init__(self):
        self.name = "Eldor"
        self.stats = type('obj', (object,), {
            'hp': 150, 'max_hp': 150, 'atk': 15, 'def_': 5, 'spd': 10, 'mana': 50
        })
        self.skills = ["skill_heavy_smash", "skill_fireball", "skill_heal_light"]
        self.ai_policy = "Player"

def main():
    print("🚀 Idle RPG v4.0 System Boot...")
    
    # Init Services
    factory = OpponentFactory()
    fx_engine = EffectEngine()
    ai_service = AIPolicyService()
    battle = BattleEngine(fx_engine, ai_service)
    
    # Load Data
    orc = factory.create_opponent("orc_brute")
    
    if orc:
        # Start Battle
        battle.start_battle(HeroMock(), orc)
    else:
        print("❌ Fehler beim Laden des Gegners.")

if __name__ == "__main__":
    main()
