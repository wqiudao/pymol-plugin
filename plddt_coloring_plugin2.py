# plddt_coloring_plugin.py
# PyMOL plugin with two coloring commands:
#
#   color_plddt [selection]
#     Color residues by CA B-factor (pLDDT, AlphaFold style)
#     b <= 50           -> #FF7E45 (orange)
#     50 < b <= 70      -> #FFDB12 (yellow)
#     70 < b <= 90      -> #57CAF9 (cyan)
#     b > 90            -> #0053D7 (blue)
#     q > 9.0 (catalytic) -> red (color only, no sphere)
#
#   color_occ [selection]
#     Color residues by CA occupancy (q), color only, no sphere
#     q == 8.99         -> red
#     q = 1,10,19,...   -> #FF7E45
#     q = 2,11,20,...   -> #FFDB12
#     q = 3,12,21,...   -> #57CAF9
#     q = 4,13,22,...   -> #0053D7
#     q = 5,14,23,...   -> #4CAF50
#     q = 6,15,24,...   -> #9B59B6
#     q = 7,16,25,...   -> #00BFA5
#     q = 8,17,26,...   -> #795548
#     q = 9,18,27,...   -> #d9d9d9
#     (cycles every 9)

from pymol import cmd


# ============================================================
# Shared utility
# ============================================================

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]


CYCLE_COLORS = [
    "#0053D7", "#FFDB12", "#9B59B6", "#57CAF9",
    "#795548", "#4CAF50", "#d9d9d9", "#00BFA5", "#FF7E45"
]

CYCLE_COLOR_NAMES = ["occ_c{}".format(i) for i in range(9)]


# ============================================================
# Command 1: color_plddt  (original logic, spheres removed)
# ============================================================

def color_plddt_by_ca(selection="all", catalytic_q_cutoff=9.0):
    """
    Color residues by CA B-factor (pLDDT) within the given selection,
    and highlight catalytic CA atoms marked by occupancy (q) with color only.

    Parameters
    ----------
    selection : str
        PyMOL selection string, e.g. "all", "myobj", "chain A".
    catalytic_q_cutoff : float
        Occupancy (q) threshold to mark catalytic CA atoms.
        Default: q > 9.0
    """
    sel = "({})".format(selection)

    for s in (
        "plddt_low_ca", "plddt_mid_ca",
        "plddt_high_ca", "plddt_veryhigh_ca", "catalytic_ca",
    ):
        try:
            cmd.delete(s)
        except Exception:
            pass

    cmd.select("plddt_low_ca",
               "{} and name CA and (b < 50.0 or b = 50.0)".format(sel))
    cmd.select("plddt_mid_ca",
               "{} and name CA and b > 50.0 and (b < 70.0 or b = 70.0)".format(sel))
    cmd.select("plddt_high_ca",
               "{} and name CA and b > 70.0 and (b < 90.0 or b = 90.0)".format(sel))
    cmd.select("plddt_veryhigh_ca",
               "{} and name CA and b > 90.0".format(sel))

    cmd.set_color("plddt_low",      hex_to_rgb("#FF7E45"))
    cmd.set_color("plddt_mid",      hex_to_rgb("#FFDB12"))
    cmd.set_color("plddt_high",     hex_to_rgb("#57CAF9"))
    cmd.set_color("plddt_veryhigh", hex_to_rgb("#0053D7"))

    cmd.color("plddt_low",      "byres plddt_low_ca")
    cmd.color("plddt_mid",      "byres plddt_mid_ca")
    cmd.color("plddt_high",     "byres plddt_high_ca")
    cmd.color("plddt_veryhigh", "byres plddt_veryhigh_ca")

    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_sampling", 14)

    cmd.select(
        "catalytic_ca",
        "{} and name CA and q > {}".format(sel, float(catalytic_q_cutoff))
    )
    if cmd.count_atoms("catalytic_ca") > 0:
        cmd.set_color("catalytic_red", [0.95, 0.05, 0.05])
        cmd.color("catalytic_red", "byres catalytic_ca")

    n_low  = cmd.count_atoms("plddt_low_ca")
    n_mid  = cmd.count_atoms("plddt_mid_ca")
    n_high = cmd.count_atoms("plddt_high_ca")
    n_vhi  = cmd.count_atoms("plddt_veryhigh_ca")
    n_cat  = cmd.count_atoms("catalytic_ca")
    print(
        "[pLDDT] CA counts in '{}': "
        "<50={}, 50-70={}, 70-90={}, >=90={} | "
        "catalytic(q>{})={}".format(
            selection, n_low, n_mid, n_high, n_vhi, catalytic_q_cutoff, n_cat
        )
    )


def color_plddt(selection="all"):
    """PyMOL command: color_plddt [selection]"""
    return color_plddt_by_ca(selection)


cmd.extend("color_plddt", color_plddt)


# ============================================================
# Command 2: color_occ  (9-color cycle + red for 8.99)
# ============================================================

def color_by_occ0(selection="all"):
    """
    Color residues by CA occupancy (q), color only, no sphere.

    Coloring rules (9-color cycle, (val-1) % 9):
      q = 1,10,19,...  -> #0053D7
      q = 2,11,20,...  -> #FFDB12
      q = 3,12,21,...  -> #9B59B6
      q = 4,13,22,...  -> #57CAF9
      q = 5,14,23,...  -> #795548
      q = 6,15,24,...  -> #4CAF50
      q = 7,16,25,...  -> #d9d9d9
      q = 8,17,26,...  -> #00BFA5
      q = 9,18,27,...  -> #FF7E45
      q == 8.99        -> red (applied last, highest priority)

    Parameters
    ----------
    selection : str
        PyMOL selection string, e.g. "all", "myobj", "chain A".
    """
    sel = "({})".format(selection)

    old_sels = ["occ_special_ca"] + ["occ_cycle_{}_ca".format(i) for i in range(9)]
    for s in old_sels:
        try:
            cmd.delete(s)
        except Exception:
            pass

    # Register colors
    cmd.set_color("occ_red", [0.95, 0.05, 0.05])
    for i, hex_col in enumerate(CYCLE_COLORS):
        cmd.set_color(CYCLE_COLOR_NAMES[i], hex_to_rgb(hex_col))

    # 8.99 special
    cmd.select("occ_special_ca",
               "{} and name CA and q > 8.98 and q < 9.0".format(sel))

    # 9-color cycle: integers 1~54 (covers 6 full cycles), grouped by (val-1) % 9
    max_occ = 54
    for ci in range(9):
        vals = [v for v in range(1, max_occ + 1) if (v - 1) % 9 == ci]
        expr = " or ".join(
            "(q > {} and q < {})".format(v - 0.01, v + 0.01) for v in vals
        )
        cmd.select(
            "occ_cycle_{}_ca".format(ci),
            "{} and name CA and ({})".format(sel, expr)
        )

    # Color by residue: cycle colors first, then red last (wins)
    for ci in range(9):
        cmd.color(CYCLE_COLOR_NAMES[ci], "byres occ_cycle_{}_ca".format(ci))
    cmd.color("occ_red", "byres occ_special_ca")

    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_sampling", 14)

    n_spec = cmd.count_atoms("occ_special_ca")
    counts = [cmd.count_atoms("occ_cycle_{}_ca".format(i)) for i in range(9)]
    print(
        "[OCC] CA counts in '{}': "
        "c0={}, c1={}, c2={}, c3={}, c4={}, c5={}, c6={}, c7={}, c8={} | "
        "red(8.99)={}".format(
            selection,
            counts[0], counts[1], counts[2], counts[3], counts[4],
            counts[5], counts[6], counts[7], counts[8],
            n_spec
        )
    )



        
def color_by_occ(selection="all", catalytic_residues=""):
    """
    Color residues by CA occupancy (q), color only, no sphere.
    Optionally mark catalytic residues with red spheres.

    Parameters
    ----------
    selection : str
        PyMOL selection string, e.g. "all", "myobj", "chain A".
    catalytic_residues : str
        Comma-separated residue numbers to mark as catalytic, e.g. "42,105,300".
        If empty, no catalytic spheres are drawn.
    """
    sel = "({})".format(selection)

    old_sels = ["occ_special_ca", "catalytic"] + ["occ_cycle_{}_ca".format(i) for i in range(9)]
    for s in old_sels:
        try:
            cmd.delete(s)
        except Exception:
            pass

    # Register colors
    cmd.set_color("occ_red", [0.95, 0.05, 0.05])
    for i, hex_col in enumerate(CYCLE_COLORS):
        cmd.set_color(CYCLE_COLOR_NAMES[i], hex_to_rgb(hex_col))

    # 8.99 special
    cmd.select("occ_special_ca",
               "{} and name CA and q > 8.98 and q < 9.0".format(sel))

    # 9-color cycle
    max_occ = 54
    for ci in range(9):
        vals = [v for v in range(1, max_occ + 1) if (v - 1) % 9 == ci]
        expr = " or ".join(
            "(q > {} and q < {})".format(v - 0.01, v + 0.01) for v in vals
        )
        cmd.select(
            "occ_cycle_{}_ca".format(ci),
            "{} and name CA and ({})".format(sel, expr)
        )

    # Color by residue: cycle colors first, then red last (wins)
    for ci in range(9):
        cmd.color(CYCLE_COLOR_NAMES[ci], "byres occ_cycle_{}_ca".format(ci))
    cmd.color("occ_red", "byres occ_special_ca")

    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_sampling", 14)

    # ── Catalytic residues: red spheres ──────────────────────────
    res_list = [r.strip() for r in catalytic_residues.split(",") if r.strip()]
    if res_list:
        resi_expr = "+".join(res_list)          # e.g. "42+105+300"
        cmd.select(
            "catalytic",
            "{} and name CA and resi {}".format(sel, resi_expr)
        )
        n_cat = cmd.count_atoms("catalytic")
        if n_cat > 0:
            cmd.show("spheres", "catalytic")
            cmd.set("sphere_scale", 1)
            cmd.set("sphere_transparency", 0.0, "catalytic")
            cmd.color("red", "catalytic")
            print("[OCC] Catalytic CA spheres: {} atom(s) at resi {}".format(
                n_cat, resi_expr))
        else:
            print("[OCC] Warning: no CA atoms found for catalytic resi {}".format(
                resi_expr))
    # ─────────────────────────────────────────────────────────────

    n_spec = cmd.count_atoms("occ_special_ca")
    counts = [cmd.count_atoms("occ_cycle_{}_ca".format(i)) for i in range(9)]
    print(
        "[OCC] CA counts in '{}': "
        "c0={}, c1={}, c2={}, c3={}, c4={}, c5={}, c6={}, c7={}, c8={} | "
        "red(8.99)={}".format(
            selection,
            counts[0], counts[1], counts[2], counts[3], counts[4],
            counts[5], counts[6], counts[7], counts[8],
            n_spec
        )
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
        print("[pLDDT] Auto coloring failed: {}".format(e))

    try:
        from pymol.plugins import addmenuitemqt
        addmenuitemqt("pLDDT Coloring (reapply)", lambda: color_plddt("all"))
        addmenuitemqt("OCC Coloring (reapply)",   lambda: color_by_occ("all"))
    except Exception:
        pass
