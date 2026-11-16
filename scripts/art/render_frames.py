"""Render sprite frames from the rigged kitten (placeholder frame source).

    Blender -b ../work/out/kitten-rigged.blend --python scripts/art/render_frames.py -- \
        --out ../work/sprites

Writes <out>/<clip>/0001.png ... at 152x152 with a transparent background and the
pet occupying ~92% of the frame height, feet centred. This exists so the 2D
pipeline (atlas + manifest + runtime) can be validated before real painted frames
exist; the visual result is identical to the 3D model.
"""

import json
import math
import sys
from pathlib import Path

import bpy

FRAME = 152
PET_FILL = 0.92
PET_HEIGHT_M = 0.19

# clip -> (fps, loop) — mirrors docs/character/SPRITE_SPEC.md
CLIPS = {
    "idle_observe": (6, True),
    "walk_in_place": (12, True),
    "sleep_enter": (8, False),
    "sleep_loop": (4, True),
    "stretch_exit": (10, False),
    "cursor_watch": (6, True),
    "pet_react": (12, False),
    "micro_groom": (6, False),
    "micro_ear_tail": (10, False),
    "intro_peek": (10, False),
}


def setup_camera(scene):
    cam_data = bpy.data.cameras.new("sprite")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = PET_HEIGHT_M / PET_FILL
    cam = bpy.data.objects.new("sprite", cam_data)
    # orbit the camera instead of translating it, otherwise the pet is cropped
    angle = math.radians(18)
    cam.location = (3 * math.sin(angle), 3 * math.cos(angle), 0.095)
    cam.rotation_euler = (math.pi / 2, 0, math.pi - angle)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    return cam


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path("sprites")
    out.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.render.resolution_x = FRAME
    scene.render.resolution_y = FRAME
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 24
    scene.view_settings.view_transform = "Standard"
    setup_camera(scene)

    arm = bpy.data.objects["PULU_rig"]
    if arm.animation_data is None:
        arm.animation_data_create()

    summary = {}
    for name, (fps, loop) in CLIPS.items():
        action = bpy.data.actions.get(name)
        if action is None:
            print("MISSING_ACTION", name)
            continue
        arm.animation_data.action = action
        start, end = action.frame_range
        duration = (end - start) / scene.render.fps
        count = max(2, round(duration * fps))
        clip_dir = out / name
        clip_dir.mkdir(parents=True, exist_ok=True)
        for i in range(count):
            frame = start + (end - start) * (i / count)
            scene.frame_set(int(round(frame)))
            scene.render.filepath = str(clip_dir / f"{i:04d}.png")
            bpy.ops.render.render(write_still=True)
        summary[name] = {"fps": fps, "loop": loop, "frames": count, "duration": round(duration, 3)}
        print(f"CLIP {name} frames={count} duration={duration:.2f}")

    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("PULU_FRAMES_DONE", out)


main()
