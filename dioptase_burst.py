#!/usr/bin/env python3
"""Dioptase Burst — neon asteroids-burst arcade for ElbowOS."""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys

import pygame

W, H = 1080, 1920
FPS = 30
TITLE = "DIOPTASE BURST"
HANDLE = "x.com/ElbowOS"
BG = (3, 18, 22)
INK = (230, 255, 248)
TEAL = (16, 230, 196)
MINT = (140, 255, 210)
GOLD = (255, 214, 70)
MAG = (255, 64, 150)
DEEP = (8, 48, 56)
PLAY_TOP, PLAY_BOT = 200, 1840


class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, vx, vy, life, col, r=4):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life, self.col, self.r = life, col, r


class Rock:
    __slots__ = ("x", "y", "vx", "vy", "r", "spin", "ang", "hp", "kind")

    def __init__(self, x, y, r, kind=0):
        a = random.random() * math.tau
        spd = random.uniform(40, 140)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * spd, math.sin(a) * spd
        self.r, self.spin = r, random.uniform(-2.4, 2.4)
        self.ang, self.hp, self.kind = random.random() * math.tau, 1, kind


class Shot:
    __slots__ = ("x", "y", "vx", "vy", "life")

    def __init__(self, x, y, ang):
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(ang) * 920, math.sin(ang) * 920
        self.life = 0.85


class Game:
    def __init__(self, record: bool):
        self.record = record
        self.surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.Font(None, 64)
        self.font_md = pygame.font.Font(None, 44)
        self.font_sm = pygame.font.Font(None, 30)
        self.score = 0
        self.reset()

    def reset(self) -> None:
        self.t = 0.0
        self.flash = 0.0
        self.hurt = 0.0
        self.combo = 1
        self.px, self.py = W * 0.5, H * 0.58
        self.pvx = self.pvy = 0.0
        self.ang = -math.pi / 2
        self.cool = 0.0
        self.alive = True
        self.respawn = 0.0
        self.shots: list[Shot] = []
        self.rocks: list[Rock] = []
        self.sparks: list[Spark] = []
        self.stars = [[random.uniform(0, W), random.uniform(0, H), random.uniform(0.5, 2.4)]
                      for _ in range(90)]
        for _ in range(6):
            self._spawn_rock(big=True)

    def _spawn_rock(self, big=False, x=None, y=None, r=None) -> None:
        if x is None:
            x = random.choice([random.uniform(80, 280), random.uniform(W - 280, W - 80)])
            y = random.uniform(PLAY_TOP + 80, PLAY_BOT - 80)
        r = r if r is not None else (random.uniform(54, 88) if big else random.uniform(22, 36))
        self.rocks.append(Rock(x, y, r, 0 if r > 40 else 1))

    def burst(self, x, y, col, n=18) -> None:
        for _ in range(n):
            a = random.random() * math.tau
            spd = random.uniform(80, 560)
            self.sparks.append(Spark(x, y, math.cos(a) * spd, math.sin(a) * spd,
                                     random.uniform(0.2, 0.55), col, random.randint(3, 8)))

    def fire(self) -> None:
        if self.cool > 0 or not self.alive:
            return
        self.cool = 0.14
        nose = 28
        sx = self.px + math.cos(self.ang) * nose
        sy = self.py + math.sin(self.ang) * nose
        self.shots.append(Shot(sx, sy, self.ang))
        self.burst(sx, sy, MINT, 5)

    def autoplay(self) -> None:
        if not self.alive:
            return
        if not self.rocks:
            return
        tgt = min(self.rocks, key=lambda r: (r.x - self.px) ** 2 + (r.y - self.py) ** 2)
        want = math.atan2(tgt.y - self.py, tgt.x - self.px)
        diff = (want - self.ang + math.pi) % math.tau - math.pi
        self.ang += max(-0.18, min(0.18, diff))
        dist = math.hypot(tgt.x - self.px, tgt.y - self.py)
        if dist > 260:
            self.pvx += math.cos(self.ang) * 18
            self.pvy += math.sin(self.ang) * 18
        if abs(diff) < 0.22 and dist < 720:
            self.fire()
        if self.px < 160:
            self.pvx += 8
        if self.px > W - 160:
            self.pvx -= 8
        if self.py < PLAY_TOP + 160:
            self.pvy += 8
        if self.py > PLAY_BOT - 160:
            self.pvy -= 8

    def _wrap(self, x, y):
        if x < 40:
            x = W - 40
        if x > W - 40:
            x = 40
        if y < PLAY_TOP:
            y = PLAY_BOT - 8
        if y > PLAY_BOT:
            y = PLAY_TOP + 8
        return x, y

    def _split(self, rock: Rock) -> None:
        self.burst(rock.x, rock.y, TEAL if rock.kind == 0 else GOLD, 22)
        self.score += int((90 if rock.r > 40 else 35) * self.combo)
        self.combo = min(9, self.combo + 1)
        self.flash = 0.10
        if rock.r > 36:
            for _ in range(2):
                nr = rock.r * 0.52
                child = Rock(rock.x + random.uniform(-12, 12),
                             rock.y + random.uniform(-12, 12), nr, 1)
                child.vx += rock.vx * 0.4
                child.vy += rock.vy * 0.4
                self.rocks.append(child)

    def update(self, dt: float) -> None:
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        self.hurt = max(0.0, self.hurt - dt)
        self.cool = max(0.0, self.cool - dt)
        if not self.alive:
            self.respawn -= dt
            if self.respawn <= 0:
                keep = self.sparks[:]
                sc = self.score
                self.reset()
                self.score, self.sparks = sc, keep
            self._tick_fx(dt)
            return
        if self.record:
            self.autoplay()
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.ang -= 3.6 * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.ang += 3.6 * dt
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.pvx += math.cos(self.ang) * 22
                self.pvy += math.sin(self.ang) * 22
            if keys[pygame.K_SPACE] or keys[pygame.K_k]:
                self.fire()
        self.pvx *= 0.985
        self.pvy *= 0.985
        self.px, self.py = self._wrap(self.px + self.pvx * dt, self.py + self.pvy * dt)
        for sh in self.shots:
            sh.x += sh.vx * dt
            sh.y += sh.vy * dt
            sh.life -= dt
            sh.x, sh.y = self._wrap(sh.x, sh.y)
        self.shots = [s for s in self.shots if s.life > 0]
        for rk in self.rocks:
            rk.x += rk.vx * dt
            rk.y += rk.vy * dt
            rk.ang += rk.spin * dt
            rk.x, rk.y = self._wrap(rk.x, rk.y)
        live = []
        for rk in self.rocks:
            hit = False
            for sh in self.shots:
                if (sh.x - rk.x) ** 2 + (sh.y - rk.y) ** 2 < (rk.r + 8) ** 2:
                    sh.life = 0
                    hit = True
                    break
            if hit:
                self._split(rk)
            else:
                live.append(rk)
        self.rocks = live
        if len(self.rocks) < 5:
            self._spawn_rock(big=random.random() < 0.55)
        for rk in self.rocks:
            if (rk.x - self.px) ** 2 + (rk.y - self.py) ** 2 < (rk.r + 16) ** 2:
                self.alive = False
                self.respawn = 0.7
                self.hurt = 0.4
                self.combo = 1
                self.burst(self.px, self.py, MAG, 36)
                break
        self._tick_fx(dt)

    def _tick_fx(self, dt: float) -> None:
        sparks = []
        for sp in self.sparks:
            sp.life -= dt
            if sp.life <= 0:
                continue
            sp.x += sp.vx * dt
            sp.y += sp.vy * dt
            sparks.append(sp)
        self.sparks = sparks
        for st in self.stars:
            st[1] += (18 + st[2] * 14) * dt
            if st[1] > H:
                st[1] = -6
                st[0] = random.uniform(0, W)

    def handle(self, ev) -> None:
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
            self.score = 0
            self.reset()

    def draw(self, s: pygame.Surface) -> None:
        s.fill(BG)
        pulse = 0.55 + 0.45 * math.sin(self.t * 2.2)
        for i in range(8):
            y = int(140 + i * 220 + math.sin(self.t * 0.6 + i) * 16)
            pygame.draw.line(s, (6, 40, 46), (0, y), (W, y), 3)
        for x, y, r in self.stars:
            pygame.draw.circle(s, (20, 80, 88), (int(x) % W, int(y) % H), int(r))
        arena = pygame.Rect(28, PLAY_TOP - 12, W - 56, PLAY_BOT - PLAY_TOP + 24)
        pygame.draw.rect(s, DEEP, arena, border_radius=22)
        pygame.draw.rect(s, TEAL, arena, 4, border_radius=22)
        for rk in self.rocks:
            pts = []
            n = 7 if rk.kind == 0 else 5
            for i in range(n):
                a = rk.ang + i * math.tau / n
                rad = rk.r * (0.78 + 0.22 * math.sin(a * 3 + rk.ang))
                pts.append((rk.x + math.cos(a) * rad, rk.y + math.sin(a) * rad))
            col = TEAL if rk.kind == 0 else GOLD
            pygame.draw.polygon(s, (10, 70, 68), pts)
            pygame.draw.polygon(s, col, pts, 4)
            pygame.draw.circle(s, MINT, (int(rk.x), int(rk.y)), max(3, int(rk.r * 0.18)))
        for sh in self.shots:
            pygame.draw.circle(s, GOLD, (int(sh.x), int(sh.y)), 7)
            pygame.draw.circle(s, INK, (int(sh.x), int(sh.y)), 3)
        if self.alive:
            ca, sa = math.cos(self.ang), math.sin(self.ang)
            nose = (self.px + ca * 30, self.py + sa * 30)
            left = (self.px + math.cos(self.ang + 2.5) * 22, self.py + math.sin(self.ang + 2.5) * 22)
            right = (self.px + math.cos(self.ang - 2.5) * 22, self.py + math.sin(self.ang - 2.5) * 22)
            glow = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*TEAL, int(60 * pulse)), (int(self.px), int(self.py)), 34)
            s.blit(glow, (0, 0))
            pygame.draw.polygon(s, INK, [nose, left, right])
            pygame.draw.polygon(s, TEAL, [nose, left, right], 3)
            if math.hypot(self.pvx, self.pvy) > 40:
                tail = (self.px - ca * 28, self.py - sa * 28)
                pygame.draw.circle(s, GOLD, (int(tail[0]), int(tail[1])), 7)
        for sp in self.sparks:
            pygame.draw.circle(s, sp.col, (int(sp.x), int(sp.y)), max(1, int(sp.r * sp.life * 2)))
        if self.flash > 0:
            fl = pygame.Surface((W, H), pygame.SRCALPHA)
            fl.fill((80, 255, 210, int(46 * self.flash / 0.10)))
            s.blit(fl, (0, 0))
        if self.hurt > 0:
            fl = pygame.Surface((W, H), pygame.SRCALPHA)
            fl.fill((255, 40, 110, int(55 * self.hurt / 0.40)))
            s.blit(fl, (0, 0))
        title = self.font_lg.render(TITLE, True, TEAL)
        s.blit(title, title.get_rect(center=(W // 2, 58)))
        handle = self.font_sm.render(HANDLE, True, GOLD)
        s.blit(handle, handle.get_rect(center=(W // 2, 108)))
        hud = self.font_md.render(f"SCORE  {self.score}    x{self.combo}", True, MINT)
        s.blit(hud, hud.get_rect(center=(W // 2, 158)))
        hint = self.font_sm.render("A/D turn  W thrust  SPACE fire  R reset   x.com/ElbowOS", True, MAG)
        s.blit(hint, hint.get_rect(center=(W // 2, H - 48)))

    def play(self) -> None:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                else:
                    self.handle(ev)
            self.update(dt)
            self.draw(self.surf)
            screen.blit(self.surf, (0, 0))
            pygame.display.flip()

    def record_mp4(self, path: str) -> None:
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart", path,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        frames = FPS * 15
        for i in range(frames):
            self.update(1.0 / FPS)
            self.draw(self.surf)
            proc.stdin.write(pygame.image.tostring(self.surf, "RGB"))
            if i % 30 == 0:
                print(f"frame {i}/{frames}", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed: {rc}")
        print("wrote", path)


def main() -> None:
    record = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
    play = "--play" in sys.argv
    if record or not play:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    g = Game(record or not play)
    if record or not play:
        out = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/DIOPTASE_BURST_ElbowOS.mp4")
        g.record_mp4(out)
    else:
        g.play()
    pygame.quit()


if __name__ == "__main__":
    main()
