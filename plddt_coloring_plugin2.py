# plddt_coloring_plugin.py
# PyMOL plugin with two coloring commands:
#
#   color_plddt [selection]
#     Color residues by CA B-factor (pLDDT, AlphaFold style)
#     b <= 50           -> orange
#     50 < b <= 70      -> yellow
#     70 < b <= 90      -> cyan
#     b > 90            -> blue
#     q > 9.0 (catalytic) -> red sphere
#
#   color_occ [selection]
#     Color residues by CA occupancy (q)
#     q == 8.99         -> pink
#     q odd integer     -> #d9d9d9
#     q even integer    -> #E8E8E8

from pymol import cmd


# ============================================================
# Shared utility
# ============================================================

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]


# ============================================================
# Command 1: color_plddt  (original, unchanged)
# ============================================================

def color_plddt_by_ca(selection="all", catalytic_q_cutoff=9.0):
    """
    Color residues by CA B-factor (pLDDT) within the given selection,
    and highlight catalytic CA atoms marked by occupancy (q).

    Parameters
    ----------
    selection : str
        PyMOL selection string, e.g. "all", "myobj", "chain A".
    catalytic_q_cutoff : float
        Occupancy (q) threshold to mark catalytic CA atoms.
        Default: q > 9.0
    """
    sel = f"({selection})"

    # Clean old temp selections
    for s in (
        "plddt_low_ca", "plddt_mid_ca",
        "plddt_high_ca", "plddt_veryhigh_ca", "catalytic_ca",
    ):
        try:
            cmd.delete(s)
        except Exception:
            pass

    # pLDDT bins (CA-based)
    cmd.select("plddt_low_ca",
               f"{sel} and name CA and (b < 50.0 or b = 50.0)")
    cmd.select("plddt_mid_ca",
               f"{sel} and name CA and b > 50.0 and (b < 70.0 or b = 70.0)")
    cmd.select("plddt_high_ca",
               f"{sel} and name CA and b > 70.0 and (b < 90.0 or b = 90.0)")
    cmd.select("plddt_veryhigh_ca",
               f"{sel} and name CA and b > 90.0")

    # AlphaFold colors
    cmd.set_color("plddt_low",      [0xFF/255, 0x7E/255, 0x45/255])
    cmd.set_color("plddt_mid",      [0xFF/255, 0xDB/255, 0x12/255])
    cmd.set_color("plddt_high",     [0x57/255, 0xCA/255, 0xF9/255])
    cmd.set_color("plddt_veryhigh", [0x00/255, 0x53/255, 0xD7/255])

    cmd.color("plddt_low",      "byres plddt_low_ca")
    cmd.color("plddt_mid",      "byres plddt_mid_ca")
    cmd.color("plddt_high",     "byres plddt_high_ca")
    cmd.color("plddt_veryhigh", "byres plddt_veryhigh_ca")

    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_sampling", 14)

    # Catalytic CA highlighting
    cmd.select(
        "catalytic_ca",
        f"{sel} and name CA and q > {float(catalytic_q_cutoff)}"
    )
    if cmd.count_atoms("catalytic_ca") > 0:
        cmd.set_color("catalytic_red", [0.95, 0.05, 0.05])
        cmd.show("spheres", "catalytic_ca")
        cmd.set("sphere_scale", 1, "catalytic_ca")
        cmd.color("catalytic_red", "catalytic_ca")
        cmd.set("depth_cue", 0)

    # Summary
    n_low = cmd.count_atoms("plddt_low_ca")
    n_mid = cmd.count_atoms("plddt_mid_ca")
    n_high = cmd.count_atoms("plddt_high_ca")
    n_vhi = cmd.count_atoms("plddt_veryhigh_ca")
    n_cat = cmd.count_atoms("catalytic_ca")
    print(
        f"[pLDDT] CA counts in '{selection}': "
        f"<50={n_low}, 50-70={n_mid}, 70-90={n_high}, >=90={n_vhi} | "
        f"catalytic(q>{catalytic_q_cutoff})={n_cat}"
    )


def color_plddt(selection="all"):
    """PyMOL command: color_plddt [selection]"""
    return color_plddt_by_ca(selection)


cmd.extend("color_plddt", color_plddt)


# ============================================================
# Command 2: color_occ  (new)
# ============================================================

def color_by_occ(selection="all"):
    """
    Color residues by CA occupancy (q) within the given selection.

    Coloring rules:
      q == 8.99        -> pink  (special marked residues)
      q odd integer    -> #d9d9d9 (light gray)
      q even integer   -> #E8E8E8 (lighter gray, alternating)

    Parameters
    ----------
    selection : str
        PyMOL selection string, e.g. "all", "myobj", "chain A".
    """
    sel = f"({selection})"

    # Clean old temp selections
    for s in ("occ_special_ca", "occ_odd_ca", "occ_even_ca"):
        try:
            cmd.delete(s)
        except Exception:
            pass

    # Define colors
    cmd.set_color("occ_pink",     hex_to_rgb("#FF9EB5"))
    cmd.set_color("occ_gray_odd", hex_to_rgb("#d9d9d9"))
    cmd.set_color("occ_gray_eve", hex_to_rgb("#E8E8E8"))

    # 8.99 special (use float range to avoid precision issues)
    cmd.select("occ_special_ca",
               f"{sel} and name CA and q > 8.98 and q < 9.0")

    # Odd/even: enumerate 1~19 (extend if needed)
    odd_vals  = list(range(1, 20, 2))
    even_vals = list(range(2, 20, 2))

    odd_expr  = " or ".join(
        f"(q > {v - 0.01} and q < {v + 0.01})" for v in odd_vals
    )
    even_expr = " or ".join(
        f"(q > {v - 0.01} and q < {v + 0.01})" for v in even_vals
    )

    cmd.select("occ_odd_ca",  f"{sel} and name CA and ({odd_expr})")
    cmd.select("occ_even_ca", f"{sel} and name CA and ({even_expr})")

    # Color entire residues by CA membership
    cmd.color("occ_gray_odd", "byres occ_odd_ca")
    cmd.color("occ_gray_eve", "byres occ_even_ca")

    # Pink special: color byres + show sphere on CA
    if cmd.count_atoms("occ_special_ca") > 0:
        cmd.color("occ_pink", "byres occ_special_ca")
        cmd.show("spheres", "occ_special_ca")
        cmd.set("sphere_scale", 1, "occ_special_ca")
        cmd.set("depth_cue", 0)

    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_sampling", 14)

    # Summary
    n_odd  = cmd.count_atoms("occ_odd_ca")
    n_eve  = cmd.count_atoms("occ_even_ca")
    n_spec = cmd.count_atoms("occ_special_ca")
    print(
        f"[OCC] CA counts in '{selection}': "
        f"odd_gray={n_odd}, even_gray={n_eve}, pink(8.99)={n_spec}"
    )


cmd.extend("color_occ", color_by_occ)


# ============================================================
# Plugin entry point
# ============================================================

def __init_plugin__(app=None):
    try:
        color_plddt()
        print("[pLDDT] Auto coloring applied (default selection: all).")
    except Exception as e:
        print(f"[pLDDT] Auto coloring failed: {e}")

    try:
        from pymol.plugins import addmenuitemqt
        addmenuitemqt("pLDDT Coloring (reapply)", lambda: color_plddt("all"))
        addmenuitemqt("OCC Coloring (reapply)",   lambda: color_by_occ("all"))
    except Exception:
        pass
```

两个命令的使用方式：
```
# 在 PyMOL 中
run plddt_coloring_plugin.py

color_plddt          # B-factor pLDDT 配色
color_plddt chain A

color_occ            # occupancy 配色
color_occ chain A
