"""Rig and animate the PULU kitten, then export a GLB with clips.

    Blender -b ../work/out/kitten-blockout-v1.blend --python scripts/character/rig_kitten.py -- --out ../work/out

Weighting is rigid (each vertex 100% on its nearest bone). At 76 px a rigid,
figurine-like deformation is preferable to bone-heat weights that can fail on the
merged, intersecting shells and produce tearing.

Bone names follow docs/milestones/m01/03_3D_ASSETS_AND_ANIMATION.md.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

FPS = 30

# name, head, tail, parent
BONES = [
    ("root",      (0.0, 0.0, 0.0),      (0.0, 0.0, 0.10),   None),
    ("pelvis",    (0.0, -0.02, 0.28),   (0.0, 0.0, 0.42),   "root"),
    ("spine_01",  (0.0, 0.0, 0.42),     (0.0, 0.03, 0.55),  "pelvis"),
    ("neck",      (0.0, 0.03, 0.55),    (0.0, 0.05, 0.62),  "spine_01"),
    ("head",      (0.0, 0.05, 0.62),    (0.0, 0.07, 0.90),  "neck"),
    ("ear_L",     (0.15, -0.01, 0.81),  (0.25, -0.03, 1.00), "head"),
    ("ear_R",     (-0.15, -0.01, 0.81), (-0.25, -0.03, 1.00), "head"),
    ("tail_01",   (0.15, -0.21, 0.33),  (0.23, -0.32, 0.24), "pelvis"),
    ("tail_02",   (0.23, -0.32, 0.24),  (0.29, -0.35, 0.12), "tail_01"),
    ("tail_03",   (0.29, -0.35, 0.12),  (0.28, 0.02, 0.07),  "tail_02"),
    ("front_upper_L", (0.10, 0.14, 0.38), (0.10, 0.15, 0.24), "spine_01"),
    ("front_lower_L", (0.10, 0.15, 0.24), (0.10, 0.16, 0.09), "front_upper_L"),
    ("front_paw_L",   (0.10, 0.16, 0.09), (0.10, 0.20, 0.03), "front_lower_L"),
    ("front_upper_R", (-0.10, 0.14, 0.38), (-0.10, 0.15, 0.24), "spine_01"),
    ("front_lower_R", (-0.10, 0.15, 0.24), (-0.10, 0.16, 0.09), "front_upper_R"),
    ("front_paw_R",   (-0.10, 0.16, 0.09), (-0.10, 0.20, 0.03), "front_lower_R"),
    ("hind_upper_L",  (0.20, 0.02, 0.30),  (0.20, 0.06, 0.16), "pelvis"),
    ("hind_lower_L",  (0.20, 0.06, 0.16),  (0.20, 0.10, 0.06), "hind_upper_L"),
    ("hind_paw_L",    (0.20, 0.10, 0.06),  (0.20, 0.15, 0.03), "hind_lower_L"),
    ("hind_upper_R",  (-0.20, 0.02, 0.30), (-0.20, 0.06, 0.16), "pelvis"),
    ("hind_lower_R",  (-0.20, 0.06, 0.16), (-0.20, 0.10, 0.06), "hind_upper_R"),
    ("hind_paw_R",    (-0.20, 0.10, 0.06), (-0.20, 0.15, 0.03), "hind_lower_R"),
]


def build_armature():
    arm = bpy.data.armatures.new("PULU_rig")
    obj = bpy.data.objects.new("PULU_rig", arm)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    created = {}
    for name, head, tail, parent in BONES:
        b = arm.edit_bones.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        created[name] = b
    for name, _, _, parent in BONES:
        if parent:
            created[name].parent = created[parent]
            created[name].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in obj.pose.bones:
        pb.rotation_mode = "XYZ"
    return obj


def nearest_bone(co, segments):
    best, best_d = None, 1e9
    for name, h, t in segments:
        ap = co - h
        ab = t - h
        denom = ab.length_squared or 1e-9
        t_ = max(0.0, min(1.0, ap.dot(ab) / denom))
        d = (ap - ab * t_).length
        if d < best_d:
            best_d, best = d, name
    return best


def bone_distance(co, h, t):
    ap = co - h
    ab = t - h
    denom = ab.length_squared or 1e-9
    u = max(0.0, min(1.0, ap.dot(ab) / denom))
    return (ap - ab * u).length


def skin(mesh_obj, arm_obj, only=None, smooth=True):
    """Rigid for props, two-bone blended weights for the coat.

    A single nearest bone tears at the neck when the head turns; blending the two
    closest bones over a short falloff keeps the junction closed at 76 px.
    """
    segments = [(n, Vector(h), Vector(t)) for n, h, t, _ in BONES
                if n != "root" and (only is None or n in only)]
    for vg in list(mesh_obj.vertex_groups):
        mesh_obj.vertex_groups.remove(vg)
    groups = {}
    for name, _, _, _ in BONES:
        if name == "root":
            continue
        groups[name] = mesh_obj.vertex_groups.new(name=name)
    for v in mesh_obj.data.vertices:
        dists = sorted(((bone_distance(v.co, h, t), n) for n, h, t in segments))[:2]
        if not smooth or len(dists) == 1:
            groups[dists[0][1]].add([v.index], 1.0, "REPLACE")
            continue
        (d0, n0), (d1, n1) = dists
        w1 = 1.0 / (d1 + 1e-4) ** 2
        w0 = 1.0 / (d0 + 1e-4) ** 2
        total = w0 + w1
        w0, w1 = w0 / total, w1 / total
        if w1 < 0.08:
            groups[n0].add([v.index], 1.0, "REPLACE")
        else:
            groups[n0].add([v.index], w0, "REPLACE")
            groups[n1].add([v.index], w1, "REPLACE")
    mod = mesh_obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_obj
    mesh_obj.parent = arm_obj


def key(obj, frame, bone, rot=None, loc=None, scale=None):
    pb = obj.pose.bones[bone]
    if rot is not None:
        pb.rotation_euler = [math.radians(a) for a in rot]
        pb.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert("location", frame=frame)
    if scale is not None:
        pb.scale = scale
        pb.keyframe_insert("scale", frame=frame)


def new_action(arm, name):
    if name in bpy.data.actions:
        bpy.data.actions.remove(bpy.data.actions[name])
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    return act


def build_actions(arm):
    arm.animation_data_create()
    R = lambda *a: a

    # ---- idle_observe: breathing, tiny head sway, tail drift
    act = new_action(arm, "idle_observe")
    for f, s in ((1, 1.0), (90, 1.018), (180, 1.0)):
        key(arm, f, "spine_01", scale=(s, s, 1.0))
    for f, r in ((1, (0, 0, 0)), (45, (1.5, 0, 2.5)), (90, (0, 0, 0)), (135, (1.0, 0, -2.0)), (180, (0, 0, 0))):
        key(arm, f, "head", rot=r)
    for f, r in ((1, (0, 0, 0)), (60, (0, 0, 5)), (120, (0, 0, -4)), (180, (0, 0, 0))):
        key(arm, f, "tail_02", rot=r)

    # ---- walk_in_place: alternating legs + body bob (seated approximation)
    act = new_action(arm, "walk_in_place")
    for f in range(1, 38, 9):
        phase = (f - 1) / 36.0
        swing = 16 * math.sin(phase * 2 * math.pi)
        key(arm, f, "front_upper_L", rot=(swing, 0, 0))
        key(arm, f, "front_upper_R", rot=(-swing, 0, 0))
        key(arm, f, "hind_upper_L", rot=(-swing * 0.4, 0, 0))
        key(arm, f, "hind_upper_R", rot=(swing * 0.4, 0, 0))
        key(arm, f, "pelvis", loc=(0, 0, 0.004 * math.sin(phase * 4 * math.pi)))
    key(arm, 37, "front_upper_L", rot=(0, 0, 0))
    key(arm, 37, "front_upper_R", rot=(0, 0, 0))

    # ---- sleep_enter / sleep_loop / stretch_exit
    act = new_action(arm, "sleep_enter")
    for f, r in ((1, (0, 0, 0)), (45, (10, 0, 0)), (60, (14, 0, 0))):
        key(arm, f, "neck", rot=r)
    for f, r in ((1, (0, 0, 0)), (45, (12, 0, 0)), (60, (16, 0, 0))):
        key(arm, f, "head", rot=r)
    key(arm, 1, "pelvis", loc=(0, 0, 0))
    key(arm, 60, "pelvis", loc=(0, 0, -0.012))

    act = new_action(arm, "sleep_loop")
    key(arm, 1, "neck", rot=(14, 0, 0))
    key(arm, 90, "spine_01", scale=(1.0, 1.0, 1.0))
    key(arm, 180, "spine_01", scale=(1.012, 1.012, 1.0))
    key(arm, 181, "spine_01", scale=(1.0, 1.0, 1.0))
    key(arm, 90, "head", rot=(16, 0, 0))
    key(arm, 180, "head", rot=(15, 0, 0))
    key(arm, 181, "head", rot=(16, 0, 0))

    act = new_action(arm, "stretch_exit")
    for f, r in ((1, (16, 0, 0)), (30, (-8, 0, 0)), (60, (0, 0, 0))):
        key(arm, f, "head", rot=r)
    for f, r in ((1, (14, 0, 0)), (30, (-4, 0, 0)), (60, (0, 0, 0))):
        key(arm, f, "neck", rot=r)
    key(arm, 1, "front_upper_L", rot=(0, 0, 0))
    key(arm, 30, "front_upper_L", rot=(-24, 0, 0))
    key(arm, 60, "front_upper_L", rot=(0, 0, 0))
    key(arm, 1, "front_upper_R", rot=(0, 0, 0))
    key(arm, 30, "front_upper_R", rot=(-24, 0, 0))
    key(arm, 60, "front_upper_R", rot=(0, 0, 0))

    # ---- cursor_watch: head follows a wide arc
    act = new_action(arm, "cursor_watch")
    for f, r in ((1, (0, 0, 0)), (30, (0, 0, 16)), (60, (0, 0, 0)), (90, (0, 0, -16)), (120, (0, 0, 0))):
        key(arm, f, "head", rot=r)
    for f, r in ((1, (0, 0, 0)), (30, (0, 0, 6)), (90, (0, 0, -6)), (120, (0, 0, 0))):
        key(arm, f, "neck", rot=r)

    # ---- pet_react: quick head tilt + ear lift
    act = new_action(arm, "pet_react")
    for f, r in ((1, (0, 0, 0)), (8, (-7, 0, 6)), (22, (-4, 0, 3)), (45, (0, 0, 0))):
        key(arm, f, "head", rot=r)
    key(arm, 8, "ear_L", rot=(0, 0, -12))
    key(arm, 45, "ear_L", rot=(0, 0, 0))

    # ---- micro_groom: head down toward the paw
    act = new_action(arm, "micro_groom")
    for f, r in ((1, (0, 0, 0)), (20, (22, 0, -8)), (45, (26, 0, -12)), (75, (18, 0, -6)), (90, (0, 0, 0))):
        key(arm, f, "head", rot=r)
    key(arm, 20, "front_upper_L", rot=(-40, 0, 0))
    key(arm, 75, "front_upper_L", rot=(-40, 0, 0))
    key(arm, 90, "front_upper_L", rot=(0, 0, 0))

    # ---- micro_ear_tail: twitch both
    act = new_action(arm, "micro_ear_tail")
    for f, r in ((1, (0, 0, 0)), (10, (0, 0, 14)), (22, (0, 0, -6)), (40, (0, 0, 0))):
        key(arm, f, "ear_R", rot=r)
    for f, r in ((1, (0, 0, 0)), (15, (0, 0, -12)), (30, (0, 0, 8)), (60, (0, 0, 0))):
        key(arm, f, "tail_03", rot=r)

    # ---- intro_peek: rise and look up
    act = new_action(arm, "intro_peek")
    key(arm, 1, "pelvis", loc=(0, 0, -0.03))
    key(arm, 25, "pelvis", loc=(0, 0, 0.004))
    key(arm, 60, "pelvis", loc=(0, 0, 0))
    key(arm, 1, "head", rot=(-10, 0, 0))
    key(arm, 25, "head", rot=(-4, 0, 0))
    key(arm, 60, "head", rot=(0, 0, 0))

    arm.animation_data.action = None


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path("out")
    out.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.render.fps = FPS

    arm = build_armature()
    fur = bpy.data.objects["PULU_fur"]
    eye = bpy.data.objects.get("PULU_eye")
    red = bpy.data.objects.get("PULU_red")

    skin(fur, arm)
    if eye:
        skin(eye, arm, only={"head"}, smooth=False)
    if red:
        skin(red, arm, only={"neck"}, smooth=False)

    build_actions(arm)

    # the model is authored at height 1.0; the spec wants 1 unit = 1 m and a
    # 0.19 m pet, so the whole hierarchy hangs off a scaled root node
    root = bpy.data.objects.new("PULU_root", None)
    bpy.context.collection.objects.link(root)
    root.scale = (0.19, 0.19, 0.19)
    arm.parent = root

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(out / "pulu-kitten-rigged.glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_nla_strips=False,
        export_frame_range=False,
        export_force_sampling=True,
        export_skins=True,
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "kitten-rigged.blend"))
    print("PULU_RIG_DONE", out)


main()
