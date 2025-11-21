import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# Simple enemies and loot tables for the roguelite adventure.
ENEMIES = {
    "slime": {"hp": 6, "power": 2},
    "crawler": {"hp": 8, "power": 3},
    "wisp": {"hp": 5, "power": 4},
    "sentinel": {"hp": 12, "power": 5},
}

LOOT_TABLE = [
    ("small potion", "heal", 6),
    ("power core", "power", 2),
    ("ether seed", "max_hp", 4),
    ("dash module", "ability", "dash"),
]


@dataclass
class Enemy:
    name: str
    hp: int
    power: int

    @classmethod
    def random(cls) -> "Enemy":
        name = random.choice(list(ENEMIES.keys()))
        stats = ENEMIES[name]
        return cls(name=name, hp=stats["hp"], power=stats["power"])


@dataclass
class Room:
    biome: str
    position: Tuple[int, int]
    requires: Optional[str] = None
    visited: bool = False
    enemy: Optional[Enemy] = None
    loot: Optional[Tuple[str, str, object]] = None

    def describe(self) -> str:
        gated = f" (requires {self.requires})" if self.requires else ""
        enemy_text = f" An angry {self.enemy.name} is here." if self.enemy else ""
        loot_text = f" You see {self.loot[0]}." if self.loot else ""
        return (
            f"[{self.biome}]{gated} - crumbling platforms twist around you."\
            f"{enemy_text}{loot_text}"
        )


@dataclass
class Player:
    hp: int = 20
    max_hp: int = 20
    power: int = 3
    abilities: Set[str] = field(default_factory=set)
    relics: List[str] = field(default_factory=list)

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def is_alive(self) -> bool:
        return self.hp > 0


class World:
    BIOMES = ["Rust Caverns", "Sunken Archives", "Crystal Hollow", "Ashen Forge"]

    def __init__(self, size: int = 5):
        self.size = size
        self.rooms: Dict[Tuple[int, int], Room] = {}
        self.generate()

    def generate(self) -> None:
        gate_positions = [(1, 0), (-1, 1), (0, -2)]
        for x in range(-(self.size // 2), self.size // 2 + 1):
            for y in range(-(self.size // 2), self.size // 2 + 1):
                biome = random.choice(self.BIOMES)
                requires = None
                if (x, y) in gate_positions:
                    requires = "dash"
                enemy = Enemy.random() if random.random() < 0.6 else None
                loot = random.choice(LOOT_TABLE) if random.random() < 0.3 else None
                self.rooms[(x, y)] = Room(
                    biome=biome, position=(x, y), requires=requires, enemy=enemy, loot=loot
                )
        # Boss room always present
        boss_pos = (self.size // 2, self.size // 2)
        self.rooms[boss_pos] = Room(
            biome="Obsidian Throne",
            position=boss_pos,
            enemy=Enemy(name="Guardian", hp=18, power=6),
            requires="dash",
        )

    def get_room(self, pos: Tuple[int, int]) -> Optional[Room]:
        return self.rooms.get(pos)

    def valid_move(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return -(self.size // 2) <= x <= self.size // 2 and -(self.size // 2) <= y <= self.size // 2


class Game:
    DIRECTIONS = {
        "n": (0, 1),
        "s": (0, -1),
        "e": (1, 0),
        "w": (-1, 0),
    }

    def __init__(self):
        self.world = World(size=5)
        self.player = Player()
        self.position = (0, 0)
        self.world.rooms[self.position].visited = True
        self.turn = 1

    def run(self) -> None:
        self._intro()
        while self.player.is_alive():
            room = self.world.get_room(self.position)
            print("\n" + room.describe())
            command = input("Action ([n/s/e/w] move, fight, loot, rest, status, quit): ").strip().lower()
            if command in self.DIRECTIONS:
                self._move(command)
            elif command == "fight":
                self._fight()
            elif command == "loot":
                self._loot()
            elif command == "rest":
                self._rest()
            elif command == "status":
                self._status()
            elif command == "quit":
                break
            else:
                print("Unknown action.")
            self.turn += 1
            if self.player.hp <= 0:
                print("You collapse among the ruins. The cycle resets...")
                break
        print("Run complete. Thanks for exploring!")

    def _intro(self) -> None:
        print("""
==== METRO RIFT ====
A compact metroidvania-inspired roguelite. Reach the Obsidian Throne
and defeat the Guardian. Rooms may require the dash ability to enter.
""")
        self._status()

    def _status(self) -> None:
        print(
            f"HP: {self.player.hp}/{self.player.max_hp} | Power: {self.player.power} | "
            f"Abilities: {', '.join(self.player.abilities) or 'none'} | Relics: {', '.join(self.player.relics) or 'none'}"
        )

    def _move(self, direction: str) -> None:
        dx, dy = self.DIRECTIONS[direction]
        new_pos = (self.position[0] + dx, self.position[1] + dy)
        if not self.world.valid_move(new_pos):
            print("A wall of void blocks your path.")
            return
        room = self.world.get_room(new_pos)
        if room and room.requires and room.requires not in self.player.abilities:
            print(f"You need {room.requires} to traverse this path.")
            return
        self.position = new_pos
        if room:
            room.visited = True
            print(f"You move to {room.biome} at {new_pos}.")
            if room.position == (self.world.size // 2, self.world.size // 2) and not room.enemy:
                print("The throne is silent; you already claimed victory this cycle.")

    def _fight(self) -> None:
        room = self.world.get_room(self.position)
        if not room or not room.enemy:
            print("Nothing to fight here.")
            return
        enemy = room.enemy
        while enemy.hp > 0 and self.player.is_alive():
            enemy.hp -= self.player.power
            print(f"You strike the {enemy.name} for {self.player.power} damage (enemy hp {enemy.hp}).")
            if enemy.hp <= 0:
                break
            self.player.take_damage(enemy.power)
            print(f"The {enemy.name} hits back for {enemy.power} damage (hp {self.player.hp}).")
        if self.player.is_alive():
            print(f"{enemy.name.capitalize()} falls apart. You feel stronger.")
            self.player.power += 1
            room.enemy = None
            # Boss drop guarantees dash
            if enemy.name == "Guardian" and "dash" not in self.player.abilities:
                self.player.abilities.add("dash")
                print("You claim the Guardian's thrusters. Dash unlocked!")
        else:
            print("Your journey ends here.")

    def _loot(self) -> None:
        room = self.world.get_room(self.position)
        if not room or not room.loot:
            print("No loot remains.")
            return
        name, effect, value = room.loot
        if effect == "heal":
            self.player.heal(int(value))
            print(f"You drink the {name} and recover {value} hp.")
        elif effect == "power":
            self.player.power += int(value)
            print(f"Power surges through you (+{value} power).")
        elif effect == "max_hp":
            self.player.max_hp += int(value)
            self.player.heal(int(value))
            print(f"Your body hardens (+{value} max hp).")
        elif effect == "ability" and isinstance(value, str):
            self.player.abilities.add(value)
            print(f"New traversal unlocked: {value}!")
        self.player.relics.append(name)
        room.loot = None

    def _rest(self) -> None:
        self.player.heal(4)
        print("You catch your breath and regain 4 hp.")


if __name__ == "__main__":
    Game().run()
