#!/usr/bin/env python3
"""Build a generic HyperFrames launch-video composition from video.json."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "video.json"
SCENE_TYPES = {"hook", "problem", "bridge", "feature", "proof", "cta"}
PALETTE_KEYS = {"background", "surface", "foreground", "muted", "accent"}
FONT_KEYS = {"display", "body", "mono"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
HEX_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def fail(message: str) -> None:
    raise ValueError(message)


def number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def asset(value: str, label: str, allowed_prefix: str) -> tuple[str, Path, bool]:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or ":" in value:
        fail(f"{label} must stay inside the repository: {value}")
    normalised = path.as_posix()
    if not normalised.startswith(allowed_prefix):
        fail(f"{label} must be inside {allowed_prefix.rstrip('/')}/")
    resolved = (ROOT / Path(*path.parts)).resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        fail(f"{label} must stay inside the repository: {value}")
    return normalised, resolved, resolved.is_file()


def load_config() -> tuple[dict, list[str]]:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("video.json is missing")
    except json.JSONDecodeError as exc:
        fail(f"video.json is invalid JSON at line {exc.lineno}: {exc.msg}")

    if not isinstance(config, dict):
        fail("video.json must contain a JSON object")
    project = config.get("project")
    scenes = config.get("scenes")
    if not isinstance(project, dict):
        fail("project must be an object")
    if not isinstance(scenes, list) or not scenes:
        fail("scenes must be a non-empty list")

    for key in ("brand", "title"):
        if not isinstance(project.get(key), str) or not project[key].strip():
            fail(f"project.{key} must be a non-empty string")
    for key in ("width", "height", "fps"):
        if not isinstance(project.get(key), int) or project[key] < 1:
            fail(f"project.{key} must be a positive integer")

    palette = project.get("palette")
    fonts = project.get("fonts")
    if not isinstance(palette, dict) or not PALETTE_KEYS.issubset(palette):
        fail(f"project.palette must define: {', '.join(sorted(PALETTE_KEYS))}")
    for key in PALETTE_KEYS:
        if not isinstance(palette[key], str) or not HEX_PATTERN.fullmatch(palette[key]):
            fail(f"project.palette.{key} must be a six-digit hex color")
    if not isinstance(fonts, dict) or not FONT_KEYS.issubset(fonts):
        fail(f"project.fonts must define: {', '.join(sorted(FONT_KEYS))}")

    ids: set[str] = set()
    total = 0.0
    capture_warnings: list[str] = []
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            fail(f"scenes[{index - 1}] must be an object")
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not ID_PATTERN.fullmatch(scene_id):
            fail(f"scenes[{index - 1}].id must use lowercase letters, digits, and hyphens")
        if scene_id in ids:
            fail(f"duplicate scene id: {scene_id}")
        ids.add(scene_id)
        if scene.get("type") not in SCENE_TYPES:
            fail(f"scene {scene_id}.type must be one of: {', '.join(sorted(SCENE_TYPES))}")
        if not isinstance(scene.get("title"), str) or not scene["title"].strip():
            fail(f"scene {scene_id}.title must be a non-empty string")
        duration = scene.get("durationSeconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not math.isfinite(duration) or duration <= 0:
            fail(f"scene {scene_id}.durationSeconds must be a positive number")
        total += float(duration)
        if scene.get("type") == "feature":
            capture_path = scene.get("capture", f"assets/captures/{scene_id}.png")
            normalised, _, exists = asset(capture_path, f"scene {scene_id}.capture", "assets/captures/")
            scene["capture"] = normalised
            if not exists:
                capture_warnings.append(normalised)
        elif scene.get("capture"):
            normalised, _, exists = asset(scene["capture"], f"scene {scene_id}.capture", "assets/captures/")
            scene["capture"] = normalised
            if not exists:
                capture_warnings.append(normalised)

    declared_total = project.get("durationSeconds")
    if declared_total is not None:
        if not isinstance(declared_total, (int, float)) or not math.isfinite(declared_total) or declared_total <= 0:
            fail("project.durationSeconds must be a positive number")
        if not math.isclose(float(declared_total), total, abs_tol=0.01):
            fail(f"project.durationSeconds is {declared_total}, but scene durations add up to {number(total)}")
    project["durationSeconds"] = total

    audio = config.get("audio", [])
    if not isinstance(audio, list):
        fail("audio must be a list")
    for index, cue in enumerate(audio, start=1):
        if not isinstance(cue, dict):
            fail(f"audio[{index - 1}] must be an object")
        cue_id = cue.get("id", f"cue-{index:02d}")
        if not isinstance(cue_id, str) or not ID_PATTERN.fullmatch(cue_id):
            fail(f"audio[{index - 1}].id must use lowercase letters, digits, and hyphens")
        cue["id"] = cue_id
        normalised, _, exists = asset(cue.get("file"), f"audio cue {cue_id}.file", "assets/sfx/")
        cue["file"] = normalised
        for key in ("startSeconds", "durationSeconds"):
            value = cue.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
                fail(f"audio cue {cue_id}.{key} must be a non-negative number")
        if cue["durationSeconds"] <= 0:
            fail(f"audio cue {cue_id}.durationSeconds must be greater than zero")
        volume = cue.get("volume", 0.12)
        if not isinstance(volume, (int, float)) or volume < 0 or volume > 1:
            fail(f"audio cue {cue_id}.volume must be between 0 and 1")
        cue["volume"] = volume
        if not exists:
            capture_warnings.append(normalised)

    return config, capture_warnings


def scene_art(scene: dict, index: int, total_scenes: int) -> str:
    scene_id = scene["id"]
    if scene["type"] == "feature":
        capture = scene["capture"]
        path = (ROOT / Path(*PurePosixPath(capture).parts)).resolve()
        if path.is_file():
            alt = html.escape(scene.get("captureAlt", scene["title"]), quote=True)
            return f'<div class="capture"><img src="{html.escape(capture, quote=True)}" alt="{alt}" /></div>'
        return (
            '<div class="capture capture-pending">'
            '<span class="capture-orbit" aria-hidden="true"></span>'
            '<p class="capture-label">REAL PRODUCT CAPTURE REQUIRED</p>'
            f'<p class="capture-path">{html.escape(capture)}</p>'
            '<p class="capture-help">Add the genuine screen here. Keep product controls and copy authentic.</p>'
            '</div>'
        )

    offset = (index * 29) % 360
    return f'''<div class="orbit-art" aria-hidden="true">
      <svg viewBox="0 0 760 500" role="presentation">
        <g class="orbit-group" transform="rotate({offset} 380 250)">
          <ellipse cx="380" cy="250" rx="285" ry="126" />
          <ellipse cx="380" cy="250" rx="206" ry="92" transform="rotate(52 380 250)" />
          <path d="M86 280 C190 60 340 425 494 172 S695 318 634 365" />
          <circle cx="110" cy="247" r="8" /><circle cx="312" cy="316" r="8" />
          <circle cx="494" cy="172" r="10" /><circle cx="634" cy="365" r="7" />
        </g>
      </svg>
      <span class="orbit-index">{index:02d} / {total_scenes:02d}</span>
    </div>'''


def scene_document(config: dict, scene: dict, index: int) -> str:
    project = config["project"]
    palette = project["palette"]
    fonts = project["fonts"]
    scene_id = scene["id"]
    composition_id = f"scene-{scene_id}"
    duration = number(float(scene["durationSeconds"]))
    total_scenes = len(config["scenes"])
    artwork = scene_art(scene, index, total_scenes)
    brand = html.escape(project["brand"])
    eyebrow = html.escape(scene.get("eyebrow", scene["type"].replace("-", " ").upper()))
    title = html.escape(scene["title"])
    support = html.escape(scene.get("support", ""))
    support_markup = f'<p class="scene-support">{support}</p>' if support else ""
    css = f'''@font-face{{font-family:"Launch Display";src:local("{fonts['display'].split(',')[0].strip()}");}}
@font-face{{font-family:"Launch Body";src:local("{fonts['body'].split(',')[0].strip()}");}}
@font-face{{font-family:"Launch Mono";src:local("{fonts['mono'].split(',')[0].strip()}");}}
*{{box-sizing:border-box}} html,body{{margin:0;width:100%;height:100%;overflow:hidden}}
body{{font-family:"Launch Body",Arial,sans-serif;background:{palette['background']}}}
#root{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden;container-type:inline-size;color:{palette['foreground']}}}
.clip{{position:absolute}}
.scene-bg{{inset:0;background:radial-gradient(ellipse at 79% 28%,{palette['surface']},transparent 48%),{palette['background']};z-index:0}}
.scene-bg::after{{content:"";position:absolute;inset:0;background:linear-gradient(140deg,transparent 20%,{palette['accent']}12);}}
.scene-grid{{inset:0;z-index:1;opacity:.16;background-image:linear-gradient({palette['foreground']}10 1px,transparent 1px),linear-gradient(90deg,{palette['foreground']}10 1px,transparent 1px);background-size:7cqw 7cqw;mask-image:linear-gradient(to bottom,rgba(0,0,0,.6),transparent 76%)}}
.scene-thread{{left:0;right:0;bottom:14%;height:1px;z-index:2;background:linear-gradient(90deg,transparent,{palette['accent']}aa,transparent)}}
.scene-art{{right:5%;top:17%;width:52%;height:64%;z-index:3;display:flex;align-items:center;justify-content:center}}
.orbit-art{{position:relative;width:100%;height:100%;display:grid;place-items:center;color:{palette['accent']}}}
.orbit-art svg{{width:100%;height:100%;overflow:visible}}
.orbit-art ellipse,.orbit-art path{{fill:none;stroke:{palette['accent']};stroke-width:2.2;opacity:.58;vector-effect:non-scaling-stroke}}
.orbit-art circle{{fill:{palette['foreground']};opacity:.88}}
.orbit-index{{position:absolute;right:6%;bottom:6%;font:500 .8cqw/1.2 "Launch Mono",monospace;letter-spacing:.16em;color:{palette['muted']}}}
.capture{{position:relative;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1.3cqw;padding:3cqw;border:1px solid {palette['accent']}55;border-radius:1.2cqw;background:{palette['surface']}aa;box-shadow:0 1.6cqw 5cqw #0003;overflow:hidden}}
.capture img{{width:100%;height:100%;object-fit:contain;border-radius:.45cqw;background:#fff}}
.capture-pending{{border-style:dashed;text-align:center}}
.capture-orbit{{position:absolute;width:26cqw;height:26cqw;border:1px solid {palette['accent']}44;border-radius:50%;box-shadow:0 0 6cqw {palette['accent']}22;pointer-events:none}}
.capture-label,.capture-path,.capture-help{{position:relative;margin:0;max-width:85%;}}
.capture-label{{font:600 .9cqw/1.2 "Launch Mono",monospace;letter-spacing:.14em;color:{palette['accent']}}}
.capture-path{{font:500 1.25cqw/1.3 "Launch Mono",monospace;color:{palette['foreground']};overflow-wrap:anywhere}}
.capture-help{{font:400 1cqw/1.4 "Launch Body",Arial,sans-serif;color:{palette['muted']}}}
.scene-copy{{left:6.4%;top:18%;width:39%;z-index:4}}
.scene-brand{{margin:0 0 3.2cqw;font:600 .82cqw/1.3 "Launch Mono",monospace;letter-spacing:.17em;color:{palette['muted']};text-transform:uppercase}}
.scene-eyebrow{{margin:0 0 1.5cqw;font:600 .92cqw/1.2 "Launch Mono",monospace;letter-spacing:.15em;color:{palette['accent']};text-transform:uppercase}}
.scene-title{{margin:0;color:{palette['foreground']};font:600 4.1cqw/1.03 "Launch Display",Georgia,serif;letter-spacing:-.035em;max-width:100%;text-wrap:balance}}
.scene-support{{margin:2.1cqw 0 0;color:{palette['muted']};font:400 1.4cqw/1.45 "Launch Body",Arial,sans-serif;max-width:95%}}
.scene-rule{{width:6cqw;height:2px;margin-top:2.7cqw;background:{palette['accent']};transform-origin:left center}}
.scene-footer{{top:5%;right:5%;z-index:5;color:{palette['muted']};font:500 .72cqw/1.25 "Launch Mono",monospace;letter-spacing:.12em;text-align:right}}
@media (max-aspect-ratio:1/1){{.scene-title{{font-size:5cqw}}.scene-copy{{width:43%}}}}
'''
    timeline = f'''window.__timelines = window.__timelines || {{}};
const timeline_{scene_id.replace('-', '_')} = gsap.timeline({{ paused: true }});
timeline_{scene_id.replace('-', '_')}.fromTo(document.querySelector("#{scene_id}-copy"), {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: .62, ease: "power3.out" }}, .08);
timeline_{scene_id.replace('-', '_')}.fromTo(document.querySelector("#{scene_id}-art"), {{ opacity: 0, scale: .95 }}, {{ opacity: 1, scale: 1, duration: .78, ease: "power2.out" }}, .16);
timeline_{scene_id.replace('-', '_')}.fromTo(document.querySelector("#{scene_id}-rule"), {{ scaleX: 0 }}, {{ scaleX: 1, duration: .48, ease: "power2.out" }}, .45);
const orbit_{scene_id.replace('-', '_')} = document.querySelector("#{scene_id}-art .orbit-group");
if (orbit_{scene_id.replace('-', '_')}) timeline_{scene_id.replace('-', '_')}.fromTo(orbit_{scene_id.replace('-', '_')}, {{ rotation: -8, transformOrigin: "50% 50%" }}, {{ rotation: 8, duration: {max(1.0, float(scene['durationSeconds']) - 1):.3f}, ease: "sine.inOut" }}, .1);
window.__timelines["{composition_id}"] = timeline_{scene_id.replace('-', '_')};
'''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(project['brand'])} · {title}</title><script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script><style>{css}</style></head><body>
<div id="root" data-composition-id="{composition_id}" data-start="0" data-duration="{duration}" data-width="{project['width']}" data-height="{project['height']}">
  <div id="{scene_id}-background" class="clip scene-bg" data-start="0" data-duration="{duration}" data-track-index="0"></div>
  <div id="{scene_id}-grid" class="clip scene-grid" data-start="0" data-duration="{duration}" data-track-index="1"></div>
  <div id="{scene_id}-thread" class="clip scene-thread" data-start="0" data-duration="{duration}" data-track-index="2"></div>
  <div id="{scene_id}-art" class="clip scene-art" data-start="0" data-duration="{duration}" data-track-index="3">{artwork}</div>
  <div id="{scene_id}-copy" class="clip scene-copy" data-start="0" data-duration="{duration}" data-track-index="4">
    <p class="scene-brand">{brand}</p><p class="scene-eyebrow">{eyebrow}</p><h1 class="scene-title">{title}</h1>{support_markup}<div id="{scene_id}-rule" class="scene-rule"></div>
  </div>
  <div id="{scene_id}-footer" class="clip scene-footer" data-start="0" data-duration="{duration}" data-track-index="5">{brand}&nbsp;&nbsp;·&nbsp;&nbsp;{index:02d} / {total_scenes:02d}<br>{number(sum(float(s['durationSeconds']) for s in config['scenes'][:index-1]))}—{number(sum(float(s['durationSeconds']) for s in config['scenes'][:index]))}s</div>
</div>
<script>{timeline}</script></body></html>
'''


def root_document(config: dict) -> str:
    project = config["project"]
    total = number(float(project["durationSeconds"]))
    start = 0.0
    clips = []
    for scene in config["scenes"]:
        duration = float(scene["durationSeconds"])
        composition_id = f"scene-{scene['id']}"
        clips.append(
            f'  <div id="{composition_id}" class="clip" data-composition-id="{composition_id}" '
            f'data-composition-src="compositions/scenes/{scene["id"]}.html" data-start="{number(start)}" '
            f'data-duration="{number(duration)}" data-track-index="1" '
            f'data-width="{project["width"]}" data-height="{project["height"]}"></div>'
        )
        start += duration
    for index, cue in enumerate(config.get("audio", []), start=1):
        clips.append(
            f'  <audio id="sfx-{cue["id"]}" src="{html.escape(cue["file"], quote=True)}" '
            f'data-start="{number(float(cue["startSeconds"]))}" '
            f'data-duration="{number(float(cue["durationSeconds"]))}" data-track-index="8" '
            f'data-volume="{number(float(cue["volume"]))}"></audio>'
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(project['brand'])} · {html.escape(project['title'])}</title>
<style>html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:{project['palette']['background']}}}#root{{position:absolute;inset:0}}</style>
</head><body><div id="root" data-composition-id="main" data-no-timeline data-start="0" data-duration="{total}" data-width="{project['width']}" data-height="{project['height']}">
{chr(10).join(clips)}
</div></body></html>
'''


def build(check_only: bool = False) -> int:
    config, missing_assets = load_config()
    if check_only:
        print(f"Config OK: {len(config['scenes'])} scenes, {number(config['project']['durationSeconds'])} seconds")
    else:
        scene_dir = ROOT / "compositions" / "scenes"
        scene_dir.mkdir(parents=True, exist_ok=True)
        for index, scene in enumerate(config["scenes"], start=1):
            target = scene_dir / f"{scene['id']}.html"
            target.write_text(scene_document(config, scene, index), encoding="utf-8")
        (ROOT / "index.html").write_text(root_document(config), encoding="utf-8")
        print(f"Built {len(config['scenes'])} scenes into index.html ({number(config['project']['durationSeconds'])}s).")
    if missing_assets:
        unique_missing = sorted(set(missing_assets))
        print(f"Capture/audio files pending: {len(unique_missing)}. Place the files locally to replace their placeholders.")
        for item in unique_missing:
            print(f"  - {item}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate video.json without generating HTML")
    args = parser.parse_args()
    try:
        return build(check_only=args.check)
    except (OSError, ValueError) as exc:
        print(f"Build error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
