# Space Survivor: Project Overview

**Space Survivor** is a high-octane, roguelike arcade shooter built with Python and Pygame. It combines classic twin-stick shooter mechanics with modern roguelike progression systems, cinematic visual effects, and dynamic difficulty scaling.

---

## 🎮 Game Description
In Space Survivor, you take control of a futuristic starfighter tasked with surviving endless waves of hostile alien fleets. As you destroy enemies, you collect **XP Gems** to level up, allowing you to choose between unique tactical upgrades that fundamentally change your playstyle.

### Key Features:
- **Advanced Movement**: Physics-driven flight with acceleration, friction, and a high-speed Dash ability.
- **Roguelike Progression**: Dynamic level-up system with unique power-ups (Triple Shot, Homing, etc.) and a persistent Meta-Progression shop.
- **Cinematic Visuals**: 5-layer parallax backgrounds with level-based Biome tinting, Screen Shake, Hit-Stop, and Floating Damage numbers.
- **Elite HUD**: Features a real-time Radar (minimap), Boss Health Bars, and a pulsing low-health Vignette.
- **Dynamic Difficulty (DDS)**: The game monitors your performance and adjusts enemy spawn rates and speed to maintain a perfect challenge.

---

## 📂 Project Structure & Line Counts

| File Path | Lines | Description |
| :--- | :---: | :--- |
| `main.py` | ~410 | Core game engine, main loop, and state management. |
| **`src/entities/`** | | **Entity System** |
| `player.py` | ~380 | Player physics, combat logic, and meta-upgrade application. |
| `Enemy.py` | ~160 | Base enemy AI with state-based chasing and strafing. |
| `EnemySpawner.py` | ~85 | Procedural wave management and Boss gating. |
| `BossEnemy.py` | ~120 | Advanced multi-phase AI for massive capital ships. |
| `Bullet.py` | ~45 | High-performance pooled projectile logic. |
| `xp_gem.py` | ~40 | Magnetic experience drops with lerp-based collection. |
| **`src/screens/`** | | **UI & Rendering** |
| `game_hud.py` | ~350 | Elite HUD (Radar, Boss Bars, XP tracking, Power-ups). |
| `menu.py` | ~90 | High-quality main menu with animated elements. |
| `parallax_bg.py` | ~80 | 5-layer depth system with level-based Biome tinting. |
| `level_up_screen.py`| ~80 | Roguelike upgrade selection interface. |
| `shop.py` | ~70 | Meta-progression store for persistent upgrades. |
| `base_overlay.py` | ~180 | Reusable UI framework for pixel-perfect buttons/panels. |
| **`src/lib/`** | | **Core Frameworks** |
| `particle_system.py`| ~140 | 15/10 VFX engine (Explosions, Trails, Damage Numbers). |
| `game_utility.py` | ~140 | Lifecycle hooks (Save/Load, Difficulty, State Logic). |
| `event_bus.py` | ~30 | Decoupled event system for juice and SFX triggers. |
| `object_pool.py` | ~40 | High-performance memory management for bullets. |
| `analytics.py` | ~60 | Lifetime stat tracking and DDS metric collection. |
| `meta_progression.py`| ~50 | Persistent JSON-based save system for upgrades. |
| **`src/powers/`** | | **Power-up Ecosystem** |
| `power_up_manager.py`| ~140 | Spawn logic and timer-based effect management. |
| `power_up_base.py` | ~80 | Abstract base for sprite-sheet animations and icons. |
| `BoltPower.py` | ~60 | The "Super" power-up (The 15/10 experience). |

---

## 🛠 Technology Stack
- **Language**: Python 3.x
- **Framework**: Pygame (Low-level 2D rendering)
- **Data**: JSON (Persistence and Meta-progression)
- **VFX**: Surface Blitting with Alpha Compositing
- **Architecture**: Modular Entity-Component-System (ECS) Lite

---

## 🚀 Performance Metrics
- **FPS**: Locked 60 (Optimized for low-end systems).
- **Memory**: Pooled objects ensure zero garbage collection stutters.
- **Scalability**: Designed to support hundreds of on-screen entities simultaneously.
