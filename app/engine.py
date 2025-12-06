
import json5
import random
import time
from .models import SkillConfig, StatusEffectConfig, EffectAction

class Combatant:
    def __init__(self, entity_data, is_player=False):
        self.name = entity_data.name
        self.is_player = is_player
        # Deep copy stats
        self.stats = type('Stats', (), {})()
        self.stats.hp = entity_data.stats.hp
        self.stats.max_hp = entity_data.stats.max_hp
        self.stats.atk = entity_data.stats.atk
        self.stats.def_ = entity_data.stats.def_
        self.stats.spd = entity_data.stats.spd
        self.stats.mana = entity_data.stats.mana
        
        self.skills = getattr(entity_data, "skills", ["basic_attack"])
        self.ai_policy = getattr(entity_data, "ai_policy", "Manual")

class EffectEngine:
    def __init__(self):
        self.skills = {}
        self.status_effects = {}
        self._load_data()

    def _load_data(self):
        try:
            with open('config/skills.json5') as f:
                raw = json5.load(f)
                for k, v in raw.items(): self.skills[k] = SkillConfig(**v)
            with open('config/effects.json5') as f:
                raw = json5.load(f)
                for k, v in raw.items(): self.status_effects[k] = StatusEffectConfig(**v)
        except FileNotFoundError:
            print("⚠️ Config files missing for EffectEngine")

    def calculate_value(self, action, source, target):
        if action.amount: return action.amount
        if action.multiplier:
            context = {"self": source.stats, "target": target.stats}
            try: return int(eval(action.multiplier, {}, context))
            except: return 0
        return 0

    def execute_skill(self, skill_id, source, target):
        skill = self.skills.get(skill_id)
        if not skill: 
            print(f"❌ Skill {skill_id} not found.")
            return

        print(f"⚡ {source.name} nutzt {skill.name}!")
        
        for action in skill.effekte:
            if random.random() > action.chance: continue
            
            if action.type == "damage":
                val = self.calculate_value(action, source, target)
                dmg = max(1, val - target.stats.def_)
                target.stats.hp -= dmg
                print(f"   💥 {dmg} Schaden. ({target.name} HP: {target.stats.hp})")
            
            elif action.type == "heal":
                val = self.calculate_value(action, source, target)
                target.stats.hp = min(target.stats.max_hp, target.stats.hp + val)
                print(f"   💚 {val} Heilung. ({target.name} HP: {target.stats.hp})")

class BattleEngine:
    def __init__(self, effect_engine, policy_service):
        self.fx = effect_engine
        self.ai = policy_service

    def execute_turn(self, active, passive):
        # AI Decision
        skill_id = "basic_attack"
        if not active.is_player:
            decision = self.ai.decide_action(active.ai_policy, active, [passive], [active])
            if decision == "heal":
                # Finde Heilskill
                for s in active.skills:
                    if "heal" in s: skill_id = s
            else:
                 # Random Attack Skill
                 attacks = [s for s in active.skills if "heal" not in s]
                 if attacks: skill_id = random.choice(attacks)
        else:
            # Mock Player Decision
            skill_id = "skill_heavy_smash" if active.stats.mana > 10 else "basic_attack"

        self.fx.execute_skill(skill_id, active, passive)

    def start_battle(self, hero_data, enemy_data):
        hero = Combatant(hero_data, is_player=True)
        enemy = Combatant(enemy_data)
        
        print(f"⚔️ BATTLE: {hero.name} vs {enemy.name}")
        while hero.stats.hp > 0 and enemy.stats.hp > 0:
            self.execute_turn(hero, enemy)
            if enemy.stats.hp <= 0: break
            self.execute_turn(enemy, hero)
            time.sleep(0.5)
            
        winner = hero.name if hero.stats.hp > 0 else enemy.name
        print(f"🏆 Sieger: {winner}")
