import pygame
from src.entities.player import Player
from src.entities.Enemy import Enemy
from src.entities.EnemySpawner import EnemySpawner
from src.audio.audio_manager import AudioManager
from src.powers.power_up_manager import PowerUpManager
from src.screens.menu import Menu
from src.screens.pause import Pause
from src.screens.restart import Restart
from src.screens.game_hud import GameHUD
from src.screens.parallax_bg import ParallaxBackground
from src.screens.level_up_screen import LevelUpScreen
from src.screens.ui.virtual_controls import VirtualControls
from src.entities.xp_gem import XPGem
from src.entities.BossEnemy import BossEnemy
from src.config.config import SKIP_MENU, GOD_MODE, GAME_FULL_SCREEN
from src.lib.particle_system import ParticleManager
from src.lib.screen_shake import ScreenShake
from src.abilities.bomb_ability import BombAbility
from src.lib.event_bus import EventBus
from src.lib.game_state import GameState
from src.entities.Bullet import Bullet
from src.lib.object_pool import ObjectPool
from src.lib.analytics import Analytics
from src.lib.meta_progression import MetaProgression
import random
import math


class Game:

    from src.lib.game_utility import (
        game_start,
        game_restart,
        game_quit,
        show_game_menu,
        pause_game,
        trigger_game_over,
        increase_difficulty,
        update_level,
        trigger_bomb,
        load_high_score,
        save_high_score,
        save_game_state,
        load_game_state,
    )

    running = True

    # game_speed = 5

    game_width = 800
    game_height = 600

    state = GameState.MENU

    game_score = 0
    game_high_score = 0
    game_level = 1
    game_mode = "level" # "level" or "endless"

    # DDS Metrics
    time_alive = 0.0
    damage_taken = 0
    shots_fired = 0
    shots_hit = 0

    enemies: list[Enemy] = []
    
    # Time scale & Camera
    time_scale = 1.0
    camera_zoom = 1.0
    target_camera_zoom = 1.0

    debug_mode = False

    def __init__(self):
        pygame.init()

        pygame.display.set_caption("SPACE SURVIVOUR")

        # Initialize clock
        self.clock = pygame.time.Clock()
        self.dt = 0

        # Game difficulty (1-3)
        self.game_difficulty = 1

        # Initialize screen
        info = pygame.display.Info()
        if GAME_FULL_SCREEN:
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h - 60)
            )
            self.game_width = info.current_w
            self.game_height = info.current_h - 50
        else:
            self.screen = pygame.display.set_mode((self.game_width, self.game_height))

        # Screen rectangle (boundary)
        self.screen_rect = self.screen.get_rect()

        # Surface for gameplay (to support screen shake)
        self.game_surface = pygame.Surface((self.game_width, self.game_height))

        # Initialize power up manager
        self.power_up_manager = PowerUpManager(self)

        # Initialize audio manager
        self.audio_manager = AudioManager()

        # Initialize systems
        self.analytics = Analytics()
        self.meta = MetaProgression()
        self.analytics.record_game_played()

        # Initialize player
        self.player = Player(self)

        # Initialize enemies
        self.enemy_spawner = EnemySpawner(self)

        # Initialize object pools
        self.player_bullet_pool = ObjectPool(Bullet, initial_size=50)
        self.enemy_bullet_pool = ObjectPool(Bullet, initial_size=200)

        # Initialize overlay screens
        self.menu_screen = Menu(self)
        self.pause_screen = Pause(self)
        self.restart_screen = Restart(self)
        from src.screens.shop import Shop
        self.shop_screen = Shop(self)
        self.level_up_screen = LevelUpScreen(self)
        self.xp_gems = []

        # Initialize HUD
        self.hud = GameHUD(self)

        # Initialize parallax background
        self.background = ParallaxBackground(self)

        # Initialize effects
        self.particle_manager = ParticleManager()
        self.screen_shake = ScreenShake()

        # Initialize Game-level abilities
        self.bomb_ability = BombAbility(self)
        
        # Virtual controls for mobile/touch
        self.virtual_controls = VirtualControls(self)
        
        # Juice / Game Feel
        self.hit_stop_timer = 0.0
        self.flash_timer = 0.0
        self.flash_duration = 0.0
        self.flash_color = (255, 255, 255)

        # Initialize Event Bus and register listeners
        self.events = EventBus()
        self._register_events()

        # Load high score
        self.load_high_score()

        # Start with menu visible (or skip to gameplay if dev flag set)
        if SKIP_MENU:
            self.game_start()
        else:
            self.audio_manager.play_menu_music()

    def _register_events(self):
        self.events.on("boss_killed", self._on_boss_killed)
        self.events.on("enemy_killed", self._on_enemy_killed)
        self.events.on("ability_used", self._on_ability_used)
        self.events.on("player_level_up", self._on_player_level_up)

        self.events.on("boss_phase2", lambda cx, cy: self.screen_shake.trigger(20, 0.5))
        self.events.on("boss_phase2", lambda cx, cy: self.particle_manager.create_explosion(cx, cy, color=(255, 0, 0), count=60))
        self.events.on("boss_phase2", lambda cx, cy: self.screen_shake.trigger(20, 0.5))
        self.events.on("boss_phase2", lambda cx, cy: self.particle_manager.create_explosion(cx, cy, color=(255, 0, 0), count=60))
        self.events.on("boss_phase2", lambda cx, cy: self.audio_manager.play_destroy_sound())

        self.events.on("player_hit", lambda: self.audio_manager.play_hurt_sound())
        self.events.on("player_hit", lambda: self.screen_shake.trigger(4, 0.1))
        self.events.on("player_hit", lambda: self.trigger_hit_stop(0.05))
        
        self.events.on("player_shoot", lambda cx, cy, angle: self.particle_manager.create_muzzle_flash(cx, cy, angle))
        self.events.on("player_shoot", lambda cx, cy, angle: self.audio_manager.play_bullet_sound())

        self.events.on("boss_spawned", lambda: self.trigger_flash((255, 0, 0), 0.5))

        self.events.on("shield_break", lambda cx, cy: self.screen_shake.trigger(15, 0.3))
        self.events.on("shield_break", lambda cx, cy: self.particle_manager.create_explosion(cx, cy, color=(100, 255, 255), count=30))
        self.events.on("shield_break", lambda cx, cy: self.audio_manager.play_destroy_sound())

    def _on_boss_killed(self, cx, cy):
        self.audio_manager.play_destroy_sound()
        self.particle_manager.create_explosion(cx, cy, color=(255, 0, 0), count=100)
        self.screen_shake.trigger(30, 1.0)
        # Drop time scale for cinematic effect
        self.time_scale = 0.2
        # Award credits
        self.meta.add_credits(50)
        self.analytics.record_kill()

    def _on_enemy_killed(self, cx, cy):
        self.audio_manager.play_destroy_sound()
        self.particle_manager.create_explosion(cx, cy, color=(255, 100, 50), count=20)
        # Award credits randomly
        if random.random() < 0.3:
            self.meta.add_credits(5)
        self.analytics.record_kill()
        
        # Spawn XP Gem
        self.xp_gems.append(XPGem(cx, cy, value=1))

    def _on_ability_used(self, ability_name):
        self.analytics.record_ability_use(ability_name)
        if ability_name == "ultimate":
            self.target_camera_zoom = 1.15
            self.time_scale = 0.5

    def _on_player_level_up(self):
        self.audio_manager.play_power_up_sound()
        self.state = GameState.LEVEL_UP
        self.level_up_screen.roll_upgrades()

    def trigger_hit_stop(self, duration):
        """Pause game logic briefly for impact (Juice)."""
        self.hit_stop_timer = duration

    def trigger_flash(self, color, duration):
        """Flash the screen with a color (Juice)."""
        self.flash_color = color
        self.flash_timer = duration
        self.flash_duration = max(0.001, duration)

    def run(self):

        while self.running:

            # Clear game surface
            self.game_surface.fill((0, 0, 0))
            self.background.draw(self.game_surface)

            shake_ox, shake_oy = self.screen_shake.get_offset()
            # Note: For real screen shake we'd usually use a surface or translate the blits.
            # Since we draw directly to self.screen, we can't easily translate everything without changing all draw calls.
            # A better way is to draw gameplay to a separate surface and blit that with offset.
            # However, for simplicity and minimal changes, I'll update the 'run' loop to update screen shake.

            events = pygame.event.get()
            # controls
            for event in events:

                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    # ESC to pause/unpause during gameplay, or quit from menu
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.pause_game()
                        elif self.state == GameState.MENU:
                            self.game_quit()

                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.PLAYING and "bomb" in self.meta.data["unlocked_abilities"]:
                            self.bomb_ability.activate()

                    if event.key == pygame.K_LSHIFT:
                        if self.state == GameState.PLAYING and "dash" in self.player.abilities:
                            self.player.abilities["dash"].activate()

                    if event.key == pygame.K_f:
                        if self.state == GameState.PLAYING and "ultimate" in self.player.abilities:
                            self.player.abilities["ultimate"].activate()

                    if event.key == pygame.K_F3:
                        self.debug_mode = not self.debug_mode

            # ── Active gameplay ───────────────────────────────────────────────
            if self.state == GameState.PLAYING:
                raw_dt = self.clock.get_time() / 1000.0
                
                # Lerp time scale back to 1.0
                self.time_scale += (1.0 - self.time_scale) * raw_dt * 1.5
                if self.time_scale > 0.99:
                    self.time_scale = 1.0
                
                # Lerp camera zoom
                self.camera_zoom += (self.target_camera_zoom - self.camera_zoom) * raw_dt * 3.0
                if self.camera_zoom > 1.0 and self.target_camera_zoom == 1.15:
                    if not hasattr(self, '_zoom_timer'):
                        self._zoom_timer = 0
                    self._zoom_timer += raw_dt
                    if self._zoom_timer > 1.5:
                        self.target_camera_zoom = 1.0
                elif self.target_camera_zoom == 1.0:
                    self._zoom_timer = 0

                # Apply time scale
                self.dt = raw_dt * self.time_scale

                # Hit Stop / Game Freeze logic
                actual_dt = self.dt
                if self.hit_stop_timer > 0:
                    self.hit_stop_timer -= raw_dt
                    if self.hit_stop_timer > 0:
                        actual_dt = 0  # Game logic completely freezes for a split second

                self.time_alive += actual_dt
                self.bomb_ability.update(actual_dt)
                
                # Update and draw player bullets
                for bullet in list(self.player_bullet_pool.get_active()):
                    bullet.update(actual_dt)
                    bullet.draw(self.game_surface)
                    if bullet.check_collision(self.enemies):
                        self.shots_hit += 1
                        bullet.deactivate()
                    elif bullet.is_off_canvas():
                        bullet.deactivate()

                # Update and draw enemy bullets
                for bullet in list(self.enemy_bullet_pool.get_active()):
                    bullet.update(actual_dt)
                    bullet.draw(self.game_surface)
                    if bullet.rect.colliderect(self.player.player_box):
                        if not GOD_MODE:
                            self.player.take_damage(bullet.damage)
                        bullet.deactivate()
                    elif bullet.is_off_canvas():
                        bullet.deactivate()

                self.increase_difficulty()
                self.update_level()
                # Move player
                self.player.move()
                self.player.player_box.clamp_ip(self.screen_rect)
                # Update center to match clamped rectangle
                self.player.cx = self.player.player_box.centerx
                self.player.cy = self.player.player_box.centery
                # Update and draw player
                self.player.update()
                self.player.draw(self.game_surface)
                self.player.shoot()

                # Update and draw power ups
                self.power_up_manager.update()
                self.power_up_manager.draw(self.game_surface)
                self.power_up_manager.check_collision(self.player)

                # Update and draw enemies
                self.enemy_spawner.update(actual_dt)

                self.particle_manager.update(actual_dt)
                self.screen_shake.update(raw_dt) # Shake continues even during hit stop

                # Update and draw XP gems
                for gem in self.xp_gems[:]:
                    gem.update(actual_dt, self.player)
                    gem.draw(self.game_surface)
                    if gem.rect.colliderect(self.player.player_box):
                        self.player.gain_xp(gem.value)
                        self.xp_gems.remove(gem)
                        self.audio_manager.play_bullet_sound()
                    elif gem.y > self.game_height + 100:
                        self.xp_gems.remove(gem)

                for enemy in self.enemies[:]:
                    enemy.update(actual_dt)
                    enemy.draw(self.game_surface)

                    # Check collision with player
                    if enemy.rect.colliderect(self.player.player_box):
                        if not GOD_MODE:
                            self.player.take_damage(enemy.give_dmg)
                        # Boss stays alive on collision — only remove normal enemies
                        if not isinstance(enemy, BossEnemy):
                            self.enemies.remove(enemy)
                        if self.player.health <= 0:
                            self.trigger_game_over()

                self.particle_manager.draw(self.game_surface)
                
                # Update virtual controls
                self.virtual_controls.update()

                # Draw HUD
                self.hud.update(self.dt)

            # ── Draw paused game underneath pause overlay ─────────────────────
            elif self.state == GameState.PAUSED:
                # Draw the frozen game state
                for bullet in self.player_bullet_pool.get_active():
                    bullet.draw(self.game_surface)
                for bullet in self.enemy_bullet_pool.get_active():
                    bullet.draw(self.game_surface)
                self.player.draw(self.game_surface)
                for enemy in self.enemies:
                    enemy.draw(self.game_surface)

            # Blit game surface to screen with shake and zoom
            if self.camera_zoom > 1.01:
                # scale game_surface
                scaled = pygame.transform.scale(self.game_surface, (int(self.game_width * self.camera_zoom), int(self.game_height * self.camera_zoom)))
                # center on player
                px, py = self.player.cx, self.player.cy
                # calc offset
                offset_x = self.game_width / 2 - px * self.camera_zoom
                offset_y = self.game_height / 2 - py * self.camera_zoom
                
                # Clamp offset so we don't see black edges
                min_x = self.game_width - scaled.get_width()
                min_y = self.game_height - scaled.get_height()
                offset_x = max(min_x, min(0, offset_x))
                offset_y = max(min_y, min(0, offset_y))
                
                self.screen.blit(scaled, (offset_x + shake_ox, offset_y + shake_oy))
            else:
                self.screen.blit(self.game_surface, (shake_ox, shake_oy))
                
            # Flash Effect
            if self.flash_timer > 0:
                self.flash_timer -= raw_dt
                alpha = max(0, int((self.flash_timer / self.flash_duration) * 255))
                if alpha > 0:
                    flash_surf = pygame.Surface((self.game_width, self.game_height), pygame.SRCALPHA)
                    flash_surf.fill((*self.flash_color, alpha))
                    self.screen.blit(flash_surf, (0, 0))

            if self.state == GameState.PLAYING:
                self.player.health_bar.draw(self.screen, self.player.health, 10, 10)
                self.hud.draw(self.screen)
                
                # Draw virtual controls on screen
                self.virtual_controls.draw(self.screen)
                
            if self.debug_mode:
                font = pygame.font.SysFont("Arial", 16)
                texts = [
                    f"FPS: {self.clock.get_fps():.1f}",
                    f"Enemies: {len(self.enemies)}",
                    f"Spawn Rate: {self.enemy_spawner.spawn_interval:.2f}s",
                    f"Bullets (P/E): {len(list(self.player_bullet_pool.get_active()))} / {len(list(self.enemy_bullet_pool.get_active()))}"
                ]
                for i, text in enumerate(texts):
                    surf = font.render(text, True, (0, 255, 0))
                    self.screen.blit(surf, (10, 50 + i * 20))
                
                # Draw hitboxes
                if self.state == GameState.PLAYING or self.state == GameState.PAUSED:
                    pygame.draw.rect(self.screen, (0, 255, 0), self.player.player_box, 1)
                    for enemy in self.enemies:
                        pygame.draw.rect(self.screen, (255, 0, 0), enemy.rect, 1)

            # ── Overlay screens ───────────────────────────────────────────────
            self.menu_screen.draw(events)
            self.pause_screen.draw(events)
            self.restart_screen.draw(events)
            self.shop_screen.draw(events)
            self.level_up_screen.draw(events)
            
            # 15/10 Edge Glow / Vignette
            self._draw_vignette()

            pygame.display.flip()
            # update delta time
            self.dt = self.clock.tick(60) / 1000.0
            self.dt = min(0.05, self.dt)

    def _draw_vignette(self):
        """Draw a cinematic edge glow that pulses with low health."""
        if self.state != GameState.PLAYING:
            return
            
        # Base alpha from health percentage
        hp_pct = self.player.health / self.player.max_health
        if hp_pct > 0.5:
            return # Only show when damaged
            
        intensity = (0.5 - hp_pct) * 2.0 # 0 to 1
        pulse = (math.sin(pygame.time.get_ticks() / 200.0) + 1) / 2
        alpha = max(0, min(255, int(intensity * 100 * pulse)))
        
        # Create vignette surface
        vig = pygame.Surface((self.game_width, self.game_height), pygame.SRCALPHA)
        # Use a large circle to fake a vignette
        pygame.draw.circle(vig, (150, 0, 0, alpha), (self.game_width//2, self.game_height//2), self.game_width, 200)
        self.screen.blit(vig, (0, 0))


if __name__ == "__main__":
    Game().run()

