# Hollow Flare: Metroidvania Roguelite Concept

## Vision
A fast-paced 2D action roguelite inspired by *Dead Cells* that emphasizes fluid movement, expressive melee combat, and layered exploration. Each run blends handcrafted traversal beats with procedural room remixing, rewarding mastery and experimentation.

## Core Pillars
- **Expressive mobility**: wall-jumps, air-dash, ground-slide, and pogo attacks let players chain movement through hazards.
- **Adaptive combat**: melee and ranged archetypes, plus elemental status effects (burn, shock, bleed) that amplify each other.
- **Run variety**: weapon blueprints, mutators, and biomes rotate each run; routes branch with risk/reward doors and optional challenges.
- **Readable telegraphs**: generous anticipation frames and clear VFX ensure fairness even at high speed.

## Core Loop
1. Start in the hub, pick a loadout (primary weapon, ranged tool, mutation).
2. Progress through biomes composed of procedurally remixed rooms with handcrafted set pieces.
3. Gather Cells to unlock blueprints and temporary meta-upgrades.
4. Fight an elite at the end of each biome; choose a branching exit.
5. Spend Cells in the hub to unlock new gear before the next run.

## Player Toolkit
- **Movement**: double-jump, wall-jump, air-dash (8-way), ledge grab, slide.
- **Combat**: three-hit melee chain, charged heavy, throwable tool (bomb/knife), and a limited-use parry.
- **Status System**: attacks inflict damage types; combining statuses yields bonuses (e.g., Burn + Shock = Overload burst).

## Enemy Archetypes
- **Lurker** (ground): patrols platforms, lunges on sight; weak to knockback.
- **Wisp** (air): hovers, fires predictable bolts; vulnerable during charge.
- **Bruiser** (elite): shielded frontal armor; baitable heavy swings open back-stab windows.

## Biomes & Progression
- **Sunken Bastion**: flooded corridors, vertical shafts, rusted ballista traps.
- **Crystalline Forge**: conveyor belts, heat vents that boost jumps, laser sentries.
- **Nocturne Gardens**: thorn pits, bouncing spores that create temporary platforms.

Each biome exposes three remixable room templates (combat, traversal, treasure). Rooms are stitched via door nodes; optional challenge rooms offer high rewards with modifiers (e.g., "no damage" chests).

## Meta Systems
- **Blueprints** unlock permanent gear pool entries.
- **Mutations** grant run-long modifiers (e.g., +1 dash, lifesteal, status synergy).
- **Cell economy**: Cells drop from elites and chests; spend between biomes.

## Art & Audio Direction
- **Visuals**: stylized pixel art with bold silhouettes and emissive highlights.
- **Animation**: snappy key poses, few transitional frames, coyote time for jumps.
- **Audio**: per-biome music layers; percussion intensifies in combat; crisp hit sfx.

## Run Retention Hooks
- Short runs (~25–35 minutes) with escalating stakes.
- Unlock quests ("parry 10 projectiles", "clear a biome without melee") feed blueprints.
- Daily seed with leaderboards; rotating mutators (gravity flip, projectile storms).

## Production Notes
- Build with an engine that supports tilemaps and deterministic seeds (Godot/Unity).
- Prioritize feel first: prototype movement and combat before content.
- Automate seeding to guarantee reproducible rooms and daily challenges.
