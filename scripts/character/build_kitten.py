"""PULU kitten · parametric blockout v1.

All dimensions are normalised to total height H = 1.0 (ground = 0, ear tip = 1).
Numbers come from the approved V05 turnaround measured by
work/measure.py -> work/turnaround-profile.json.

Run headless:
    Blender -b --python build_kitten.py -- --out ../out --render
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

# ---------------------------------------------------------------- proportions
# z heights (fraction of H)
Z_GROUND = 0.000
Z_BELL = 0.468
Z_COLLAR = 0.530
Z_CHIN = 0.593
Z_NOSE = 0.656
Z_EYE = 0.741
Z_HEAD_WIDE = 0.700
Z_CROWN = 0.930
Z_EAR_TIP = 1.000

# half widths (fraction of H)
HW_HAUNCH = 0.350
HW_NECK = 0.222
HW_HEAD = 0.284
EYE_DX = 0.088          # half distance between eye centres
EYE_R = 0.052

# depth (Y, +Y = facing direction), fraction of H
Y_NOSE = 0.304
Y_HEAD_BACK = -0.116
Y_CHEST = 0.287
Y_BACK = -0.257
Y_BODY_C = (Y_CHEST + Y_BACK) / 2
Y_HEAD_C = (Y_NOSE + Y_HEAD_BACK) / 2

SEG = 32


def ellipse_ring(z, hw, y_front, y_back, seg=SEG):
    """One horizontal cross-section. y_front/y_back are absolute Y extents."""
    cy = (y_front + y_back) / 2.0
    ry = (y_front - y_back) / 2.0
    pts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        pts.append((hw * math.sin(a), cy + ry * math.cos(a), z))
    return pts


def loft(name, rings, cap_bottom=True, cap_top=True):
    """rings: list of vertex lists, each with the same length. Builds quads."""
    seg = len(rings[0])
    verts = [v for ring in rings for v in ring]
    faces = []
    for r in range(len(rings) - 1):
        for i in range(seg):
            a = r * seg + i
            b = r * seg + (i + 1) % seg
            c = (r + 1) * seg + (i + 1) % seg
            d = (r + 1) * seg + i
            faces.append((a, b, c, d))
    if cap_bottom:
        faces.append(tuple(range(seg - 1, -1, -1)))
    if cap_top:
        base = (len(rings) - 1) * seg
        faces.append(tuple(range(base, base + seg)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def smooth(obj, levels=1):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if levels:
        mod = obj.modifiers.new("subd", "SUBSURF")
        mod.levels = levels
        mod.render_levels = levels
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)


def mat(name, rgb, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*rgb, 1)
    return m


# ------------------------------------------------------------------- shapes
def superell(u, p):
    return math.copysign(abs(u) ** p, u)


def build_head():
    HW, RY, YC = 0.302, 0.206, 0.088
    ZC, RZ = 0.750, 0.168
    P = 0.88
    bpy.ops.mesh.primitive_uv_sphere_add(segments=56, ring_count=40, radius=1.0)
    obj = bpy.context.object
    obj.name = "Head"
    me = obj.data
    for v in me.vertices:
        ux, uy, uz = v.co
        z = ZC + uz * RZ
        cheek = math.exp(-((z - 0.672) / 0.055) ** 2) * (abs(ux) ** 1.3)
        jaw = 1.0 - 0.11 * math.exp(-((z - 0.598) / 0.032) ** 2)
        v.co = (superell(ux, P) * HW * (1.0 + 0.048 * cheek) * jaw,
                YC + superell(uy, P) * RY,
                z)
    for v in me.vertices:
        front = max(0.0, (v.co.y - YC) / RY)
        v.co.y -= 0.026 * front ** 2
        dz = (v.co.z - 0.655) / 0.048
        g = math.exp(-dz * dz) * front ** 4
        v.co.y += 0.020 * g
        v.co.z -= 0.003 * g
        dz2 = (v.co.z - 0.780) / 0.038
        v.co.y += 0.012 * math.exp(-dz2 * dz2) * front ** 3
    me.update()
    bpy.ops.object.shade_smooth()
    return obj


def build_muzzle():
    """Two cheek pads + chin: gives the face a readable snout at small sizes."""
    parts = []
    for s in (-1, 1):
        parts.append(sphere(f"Muzzle{'LR'[s > 0]}", (0.052 * s, 0.268, 0.652),
                            0.072, (1.10, 0.78, 0.74), 24, 16))
    parts.append(sphere("Chin", (0, 0.238, 0.610), 0.062, (1.25, 0.80, 0.55), 24, 16))
    return parts


def sphere(name, loc, radius, scale=(1, 1, 1), segments=28, rings=18):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    return o


def build_body():
    profile = [
        (0.010, 0.246, 0.132, -0.150),
        (0.055, 0.288, 0.180, -0.212),
        (0.105, 0.318, 0.216, -0.244),
        (0.165, 0.338, 0.238, -0.262),
        (0.225, 0.346, 0.250, -0.270),
        (0.290, 0.336, 0.256, -0.266),
        (0.350, 0.316, 0.260, -0.254),
        (0.410, 0.288, 0.264, -0.236),
        (0.460, 0.258, 0.268, -0.208),
        (0.510, 0.230, 0.266, -0.178),
        (0.555, 0.208, 0.252, -0.150),
        (0.600, 0.192, 0.230, -0.124),
        (0.640, 0.176, 0.205, -0.100),
    ]
    rings = [ellipse_ring(z, hw, yf, yb) for z, hw, yf, yb in profile]
    obj = loft("Body", rings, cap_bottom=True, cap_top=True)
    smooth(obj, 1)
    me = obj.data
    for v in me.vertices:
        front = max(0.0, v.co.y / 0.27)
        g = math.exp(-((v.co.z - 0.470) / 0.070) ** 2) * front ** 2
        v.co.y += 0.020 * g
        v.co.x *= 1.0 + 0.018 * g
    me.update()
    return obj


def build_ear(side):
    s = side
    base = Vector((0.150 * s, -0.008, 0.800))
    tip = Vector((0.252 * s, -0.034, 1.000))
    base_hw, depth = 0.112, 0.044
    rings = []
    n = 9
    for i in range(n):
        t = i / (n - 1)
        c = base.lerp(tip, t)
        hw = base_hw * (1.0 - t ** 1.45) ** 0.8
        d = depth * (1.0 - t) ** 0.5 + 0.005
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            ring.append((c.x + hw * math.sin(a), c.y + d * math.cos(a), c.z))
        rings.append(ring)
    obj = loft(f"Ear{'LR'[s > 0]}", rings, cap_bottom=True, cap_top=True)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    return obj


def build_eye(side):
    return sphere(f"Eye{'LR'[side > 0]}", (EYE_DX * side, 0.303, Z_EYE), EYE_R,
                  (1.0, 0.62, 1.02))


def build_nose():
    return sphere("Nose", (0, 0.318, 0.664), 0.030, (1.0, 0.48, 0.58), 20, 12)


def build_collar():
    bpy.ops.mesh.primitive_torus_add(major_radius=0.240, minor_radius=0.011,
                                     major_segments=48, minor_segments=10,
                                     location=(0, 0.058, Z_COLLAR))
    obj = bpy.context.object
    obj.name = "Collar"
    obj.scale = (1.0, 0.955, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    return obj


def build_bell():
    return sphere("Bell", (0, 0.276, 0.489), 0.044, (1.0, 0.95, 1.0), 24, 16)


def build_leg(side, front=True):
    s = side
    if front:
        x0, y0 = 0.100 * s, 0.148
        top, bottom = 0.380, 0.010
        r_top, r_mid, r_bot = 0.080, 0.072, 0.084
    else:
        x0, y0 = 0.205 * s, 0.050
        top, bottom = 0.270, 0.010
        r_top, r_mid, r_bot = 0.115, 0.098, 0.088
    rings = []
    n = 10
    for i in range(n):
        t = i / (n - 1)
        z = top + (bottom - top) * t
        r = r_top + (r_mid - r_top) * min(1.0, t * 2.0)
        if t > 0.6:
            r = r_mid + (r_bot - r_mid) * (t - 0.6) / 0.4
        ring = []
        for j in range(18):
            a = 2 * math.pi * j / 18
            fy = 1.0 + 0.30 * max(0.0, math.cos(a)) * (t ** 2)
            ring.append((x0 + r * math.sin(a), y0 + r * fy * math.cos(a), z))
        rings.append(ring)
    name = f"{'Front' if front else 'Hind'}Leg{'LR'[s > 0]}"
    obj = loft(name, rings, cap_bottom=True, cap_top=True)
    smooth(obj, 1)
    return obj


def build_toes(side, front=True):
    s = side
    if front:
        x0, y0, z, r = 0.100 * s, 0.205, 0.030, 0.030
    else:
        x0, y0, z, r = 0.205 * s, 0.115, 0.028, 0.033
    out = []
    for k, dx in enumerate((-0.042, 0.0, 0.042)):
        out.append(sphere(f"{'F' if front else 'H'}Toe{s}{k}", (x0 + dx, y0, z), r,
                          (1.0, 1.15, 0.85), 16, 10))
    return out


def build_tail():
    pts = [
        (0.180, -0.180, 0.360),
        (0.244, -0.244, 0.262),
        (0.286, -0.238, 0.160),
        (0.298, -0.156, 0.098),
        (0.286, -0.060, 0.078),
        (0.252,  0.020, 0.076),
    ]
    radii = [0.058, 0.057, 0.055, 0.053, 0.050, 0.045]
    rings = []
    for i, (cx, cy, cz) in enumerate(pts):
        r = radii[i]
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            ring.append((cx + r * math.cos(a), cy + r * math.sin(a),
                         cz + r * 0.88 * math.sin(a)))
        rings.append(ring)
    obj = loft("Tail", rings, cap_bottom=True, cap_top=True)
    smooth(obj, 1)
    return obj


# ------------------------------------------------------------------- scene
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def studio():
    world = bpy.data.worlds.new("W")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.95, 0.95, 0.95, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def make_cameras():
    cams = {}
    # camera looks along its local -Z; +Y is the cat's facing direction
    for name, rot, loc in (
        ("Front", (math.pi / 2, 0, math.pi), (0, 3, 0.5)),
        ("Side", (math.pi / 2, 0, math.pi / 2), (3, 0, 0.5)),
        ("Back", (math.pi / 2, 0, 0), (0, -3, 0.5)),
    ):
        cam_data = bpy.data.cameras.new(name)
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = 1.25
        cam = bpy.data.objects.new(name, cam_data)
        cam.location = loc
        cam.rotation_euler = rot
        bpy.context.collection.objects.link(cam)
        cams[name] = cam
    return cams


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path("out")
    out.mkdir(parents=True, exist_ok=True)

    clear()
    studio()
    clay = mat("clay", (0.62, 0.61, 0.60), 0.55)
    dark = mat("eye", (0.05, 0.045, 0.04), 0.25)
    pink = mat("nose", (0.72, 0.45, 0.42), 0.5)
    red = mat("red", (0.55, 0.05, 0.03), 0.35)

    parts = []
    parts.append((build_head(), clay))
    parts.append((build_body(), clay))
    for m in build_muzzle():
        parts.append((m, clay))
    for s in (-1, 1):
        parts.append((build_ear(s), clay))
        parts.append((build_eye(s), dark))
        parts.append((build_leg(s, True), clay))
        parts.append((build_leg(s, False), clay))
        for t in build_toes(s, True):
            parts.append((t, clay))
        for t in build_toes(s, False):
            parts.append((t, clay))
    parts.append((build_nose(), pink))
    parts.append((build_collar(), red))
    parts.append((build_bell(), red))
    parts.append((build_tail(), clay))

    for obj, m in parts:
        obj.data.materials.append(m)

    # ground shadow catcher plane is deliberately omitted: silhouette check only

    cams = make_cameras()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.film_transparent = True
    scene.render.resolution_x = 600
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.color_type = "MATERIAL"
    shading.show_cavity = True
    shading.cavity_type = "BOTH"

    if "--render" in argv:
        for name, cam in cams.items():
            scene.camera = cam
            scene.render.filepath = str(out / f"blockout-{name.lower()}.png")
            bpy.ops.render.render(write_still=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(out / "kitten-blockout-v1.blend"))
    print("PULU_BLOCKOUT_DONE", out)


main()
