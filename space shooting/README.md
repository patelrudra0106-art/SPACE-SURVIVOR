<p align="center">
  <img src="assets/images/readme/hero_banner.png" alt="Space Survivor High-Detail Banner" width="100%">
</p>

# 🌌 Space Survivor
### *The Ultimate Roguelike Arcade Experience*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame 2.0+](https://img.shields.io/badge/Pygame-2.0+-4B8BBE?style=for-the-badge&logo=pygame&logoColor=white)](https://www.pygame.org/)
[![Architecture: Modular](https://img.shields.io/badge/Architecture-Modular-FFD700?style=for-the-badge)](https://github.com/yourusername/space-survivor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Space Survivor** is a high-octane, features-complete roguelike space shooter built from the ground up using Python and the Pygame library. It represents a professional approach to 2D game development, focusing on modularity, performance, and immersive "game feel."

---

## 📖 Table of Contents
1.  [Core Gameplay Pillars](#-core-gameplay-pillars)
2.  [The Roguelike Loop](#-the-roguelike-loop)
3.  [The Bestiary](#-the-bestiary)
4.  [Power-ups & Abilities](#-power-ups--abilities)
5.  [Technical Architecture](#-technical-architecture)
6.  [Project Structure](#-project-structure)
7.  [Installation & Setup](#-installation--setup)
8.  [Controls Guide](#-controls-guide)
9.  [Mobile & Touch Support](#-mobile--touch-support)
10. [FAQ](#-faq)
11. [Troubleshooting](#-troubleshooting)
12. [Contributing](#-contributing)
13. [Visual Showcase](#-visual-showcase)

---

## 🚀 Core Gameplay Pillars

### 📈 Dynamic Difficulty Scaling (DDS)
Unlike standard shooters, Space Survivor's intensity is governed by a real-time difficulty engine. It monitors your performance metrics—including combat accuracy, survival time, and health-to-damage ratios—to adjust enemy spawn rates and stats. This ensures a "flow state" experience for players of all skill levels.

### 🕹️ The "15/10" Game Feel
We prioritize tactile feedback and visual "juice":
*   **Hit-Stop & Screen-Shake**: Frame-perfect hit-pauses and procedural shake for maximum impact.
*   **Cinematics**: Dynamic time-scaling and camera zoom during epic boss deaths and ultimates.
*   **VFX Particle Engine**: A custom particle system capable of handling thousands of objects for explosions, engine trails, and projectile impacts with zero performance drop.

### 📱 Mobile & Touch Support
The game is now fully playable on mobile and touch devices!
*   **Virtual Joystick**: 360-degree movement control on the left side of the screen.
*   **Tactical Buttons**: Dedicated on-screen buttons for Dash, Ultimate, and Shooting.
*   **Multi-Input**: Works seamlessly alongside Keyboard and Mouse controls.

---

## 🔄 The Roguelike Loop

### Mid-Run Progression
As you destroy enemies, you collect **XP Gems**. Filling your XP bar triggers a **Level Up**, letting you choose from randomized tactical upgrades:
*   **Offense**: Triple Shot, Homing Missiles, Chain Lightning (Bolt Power).
*   **Defense**: Energy Shields, Max Health Boosts, Health Regeneration.

### Meta-Progression (The Shop)
Credits earned during missions can be spent in the Shop for permanent upgrades:
*   **Hull Integrity**: Permanent increases to your starting health.
*   **Fire Rate**: Meta-upgrades to your weapon's cooldown.
*   **Special Abilities**: Unlock the **Dash** and **Ultimate Beam** for future runs.

---

## 👾 The Bestiary

| Enemy Type | Description | Preview |
| :--- | :--- | :---: |
| **Normal Scout** | Reliable chasers that attempt to swarm the player. | <img src="assets/images/readme/enemy_preview.png" width="80"> |
| **Bullet Enemy** | Marksmen that keep their distance while firing aimed projectiles. | <img src="assets/images/enemies/shooting_enemy.png" width="80"> |
| **Tank Enemy** | High health pools and heavy armor; acts as mobile cover. | <img src="assets/images/enemies/enemy.png" width="80"> |
| **Boss Dreadnought** | Massive command ships with multi-phase combat logic. | <img src="assets/images/readme/boss_preview.png" width="100"> |

---

## 🏛️ Technical Architecture

### Event-Driven Design
The core engine uses an **Event Bus** to decouple gameplay logic from UI and SFX. For example, when a player takes damage, the `Player` class emits an event that the `AudioManager`, `HUD`, and `VFXManager` handle independently.

### High-Performance Object Pooling
To maintain a consistent 60+ FPS, we use **Object Pooling** for all projectiles and particles. Instead of costly object instantiation during combat, the engine recycles inactive objects from a pre-allocated memory pool.

### Parallax Biome System
A 5-layer background system that dynamically shifts tints, star density, and planet assets based on the current sector (level), creating a sense of vast movement and progression.

---

## 📁 Project Structure

```text
space-shooting/
├── assets/                 # All game resources
│   ├── audio/              # SFX and Music tracks
│   ├── fonts/              # Custom game fonts
│   └── images/             # Sprites, Backgrounds, and UI
│       ├── background/     # Parallax layer assets
│       ├── bosses/         # Dreadnought sprites
│       ├── player/         # Health-based player ships
│       └── readme/         # Visual documentation assets
├── src/                    # Core source code
│   ├── abilities/          # Dash, Ultimate, and Bomb logic
│   ├── audio/              # AudioManager implementation
│   ├── config/             # Constants and game settings
│   ├── entities/           # Player, Enemies, Bullets, XP Gems
│   ├── lib/                # Shared utilities (Pools, Particles, Events)
│   ├── powers/             # Power-up classes and Manager
│   └── screens/            # UI, Menu, Shop, and HUD overlays
└── main.py                 # Game entry point
```

---

## 🎮 Controls Guide

| Action | Key / Input | Touch / Mobile |
| :--- | :--- | :--- |
| **Movement** | `W`, `A`, `S`, `D` | Left Joystick |
| **Aiming** | `Mouse` | Automatic (Joystick Dir) |
| **Primary Fire** | `Left Click` | "FIRE" Button |
| **Dash** | `Space` | "DASH" Button |
| **Ultimate** | `E` | "ULT" Button |
| **Pause** | `P` / `ESC` | System Back / Menu |

---

## 🛠️ Installation & Setup

1.  **Requirements**: Python 3.10+ and Pygame 2.0+.
2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/space-survivor.git
    cd space-survivor
    ```
3.  **Install Dependencies**:
    ```bash
    pip install pygame
    ```
4.  **Run the Game**:
    ```bash
    python main.py
    ```

---

## ❓ FAQ

**Q: How do I unlock the Ultimate Beam?**
A: Collect credits during runs and purchase the "Ultimate Core" in the Shop menu.

**Q: Is there mobile/touch support?**
A: **Yes!** The game now features on-screen virtual controls. You can move with the joystick and use dedicated buttons for shooting and abilities.

**Q: Is there controller support?**
A: Currently Mouse + Keyboard or Touch/Mouse controls. Gamepad support is planned.

**Q: My game is lagging. What should I do?**
A: Ensure your GPU drivers are updated and you're running Python in a high-performance mode.

---

## 🔧 Troubleshooting

*   **Screen Flickering**: Ensure `GAME_FULL_SCREEN` is set appropriately in `src/config/config.py`.
*   **Audio Issues**: Verify that the `assets/audio/` folder contains all necessary `.wav` and `.mp3` files.
*   **Crash on Startup**: Run `pip install --upgrade pygame` to ensure you have the latest library version.

---

## 🤝 Contributing
Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

---

## 🖼️ Visual Showcase

<p align="center">
  <img src="assets/images/readme/background_preview.png" alt="Nebula Background" width="45%">
  <img src="assets/images/readme/player_preview.png" alt="Player Ship" width="45%">
</p>

---

<p align="center">
  <img src="assets/images/readme/player_preview.png" width="60"><br>
  <i>Developed with a focus on modularity, performance, and player engagement.</i><br>
  <b>MIT License © 2026 Space Survivor Team</b>
</p>
