# plddt_coloring_plugin.py
# PyMOL plugin/command: color residues by pLDDT stored in B-factor on CA atoms
#
# Usage in PyMOL:
#   run plddt_coloring_plugin.py
#   color_plddt                 # default == color_plddt all
#   color_plddt myobj
#   color_plddt "chain A"
#
# Ranges (non-overlapping):
#   b <= 50            -> red
#   50 < b <= 70      -> yellow
#   70 < b <= 90      -> cyan
#   b > 90           -> blue
#
# Notes:
# - Assumes pLDDT is stored in B-factor field (common in AlphaFold PDBs).
# - Uses CA atoms to decide residue bin, then colors whole residue (byres).
from pymol import cmd

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

    # ----------------------------
    # Clean old temp selections
    # ----------------------------
    for s in (
        "plddt_low_ca",
        "plddt_mid_ca",
        "plddt_high_ca",
        "plddt_veryhigh_ca",
        "catalytic_ca",
        # NEW (surface patch helpers)
        "catalytic_res",
        "catalytic_patch",
    ):
        try:
            cmd.delete(s)
        except Exception:
            pass

    # ----------------------------
    # pLDDT bins (CA-based)
    # ----------------------------
    cmd.select("plddt_low_ca",
               f"{sel} and name CA and (b < 50.0 or b = 50.0)")
    cmd.select("plddt_mid_ca",
               f"{sel} and name CA and b > 50.0 and (b < 70.0 or b = 70.0)")
    cmd.select("plddt_high_ca",
               f"{sel} and name CA and b > 70.0 and (b < 90.0 or b = 90.0)")
    cmd.select("plddt_veryhigh_ca",
               f"{sel} and name CA and b > 90.0")

    # ----------------------------
    # Define colors (AlphaFold style)
    # ----------------------------
    cmd.set_color("plddt_low",      [0xFF/255, 0x7E/255, 0x45/255])
    cmd.set_color("plddt_mid",      [0xFF/255, 0xDB/255, 0x12/255])
    cmd.set_color("plddt_high",     [0x57/255, 0xCA/255, 0xF9/255])
    cmd.set_color("plddt_veryhigh", [0x00/255, 0x53/255, 0xD7/255])

    # ----------------------------
    # Color entire residues by CA membership
    # ----------------------------
    cmd.color("plddt_low",      "byres plddt_low_ca")
    cmd.color("plddt_mid",      "byres plddt_mid_ca")
    cmd.color("plddt_high",     "byres plddt_high_ca")
    cmd.color("plddt_veryhigh", "byres plddt_veryhigh_ca")

    # Cartoon style tweaks
    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_sampling", 14)

    # ----------------------------
    # Catalytic CA highlighting (occupancy = q)
    # ----------------------------
    cmd.select(
        "catalytic_ca",
        f"{sel} and name CA and q > {float(catalytic_q_cutoff)}"
    )

    if cmd.count_atoms("catalytic_ca") > 0:
        cmd.show("spheres", "catalytic_ca")
        cmd.set("sphere_scale", 1, "catalytic_ca")
        cmd.color("red", "catalytic_ca")

    # ======================================================================
    # NEW PART (only add, do not modify existing behavior)
    # ======================================================================

    # ----------------------------
    # 1) Local electrostatic surface (PyMOL built-in)
    # ----------------------------
    # Show surface and color by electrostatics (Coulombic approximation)
    cmd.show("surface", sel)
    cmd.set("surface_quality", 1, sel)
    cmd.set("surface_color", "electrostatic", sel)

    # Slight transparency so patches are visible
    cmd.set("surface_transparency", 0.15, sel)

    # ----------------------------
    # 2) Catalytic surface patch (yellow,凸显)
    # ----------------------------
    if cmd.count_atoms("catalytic_ca") > 0:
        # Take whole residues containing catalytic CA
        cmd.select("catalytic_res", "byres catalytic_ca")

        # Create an independent surface patch object
        cmd.create("catalytic_patch", "catalytic_res")

        # Show patch as surface and force color (override electrostatics)
        cmd.show("surface", "catalytic_patch")
        cmd.color("yellow", "catalytic_patch")

        # Make the patch stand out
        cmd.set("surface_mode", 1, "catalytic_patch")
        cmd.set("surface_quality", 1, "catalytic_patch")
        cmd.set("transparency", 0.0, "catalytic_patch")

    # ----------------------------
    # Summary
    # ----------------------------
    n_low  = cmd.count_atoms("plddt_low_ca")
    n_mid  = cmd.count_atoms("plddt_mid_ca")
    n_high = cmd.count_atoms("plddt_high_ca")
    n_vhi  = cmd.count_atoms("plddt_veryhigh_ca")
    n_cat  = cmd.count_atoms("catalytic_ca")

    print(
        f"[pLDDT] CA counts in '{selection}': "
        f"<50={n_low}, 50–70={n_mid}, 70–90={n_high}, >=90={n_vhi} | "
        f"catalytic(q>{catalytic_q_cutoff})={n_cat}"
    )

# ---- Command wrapper: allow calling without args (defaults to 'all')
def color_plddt(selection="all"):
    """
    PyMOL command entry: color_plddt [selection]
    If no selection is provided, defaults to 'all'.
    """
    return color_plddt_by_ca(selection)

# Register command
cmd.extend("color_plddt", color_plddt)

def __init_plugin__(app=None):
    """
    Plugin entry point. Adds a menu item and (optionally) auto-applies coloring.

    - Menu: Plugin -> pLDDT Coloring (reapply) -> recolor all
    - Auto-color on plugin load: enabled below
    """
    # Optional: auto-apply on plugin load (keeps your manual command too)
    try:
        color_plddt()  # defaults to "all"
        print("[pLDDT] Auto coloring applied (default selection: all).")
    except Exception as e:
        print(f"[pLDDT] Auto coloring failed: {e}")

    # Add a menu item for quick re-apply
    try:
        from pymol.plugins import addmenuitemqt
        addmenuitemqt("pLDDT Coloring (reapply)", lambda: color_plddt("all"))
    except Exception:
        # Older builds may not support Qt menu helper; command still works.
        pass
