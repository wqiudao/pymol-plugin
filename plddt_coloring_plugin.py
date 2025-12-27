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
#   b < 50            -> red
#   50 <= b < 70      -> yellow
#   70 <= b < 90      -> cyan
#   b >= 90           -> blue
#
# Notes:
# - Assumes pLDDT is stored in B-factor field (common in AlphaFold PDBs).
# - Uses CA atoms to decide residue bin, then colors whole residue (byres).

from pymol import cmd

def color_plddt_by_ca(selection="all"):
    """
    Color residues by CA B-factor (pLDDT) within the given selection.

    Parameters
    ----------
    selection : str
        PyMOL selection string, e.g. "all", "myobj", "chain A", "polymer.protein".
    """
    sel = f"({selection})"

    # Remove previous temp selections (safe if not present)
    for s in ("plddt_low_ca", "plddt_mid_ca", "plddt_high_ca", "plddt_veryhigh_ca"):
        try:
            cmd.delete(s)
        except Exception:
            pass

    # Define bins based on CA atom B-factor (pLDDT)
    cmd.select("plddt_low_ca",      f"{sel} and name CA and b < 50.0")
    cmd.select("plddt_mid_ca",      f"{sel} and name CA and (b > 50.0 or b = 50.0) and b < 70.0")
    cmd.select("plddt_high_ca",     f"{sel} and name CA and (b > 70.0 or b = 70.0) and b < 90.0")
    cmd.select("plddt_veryhigh_ca", f"{sel} and name CA and (b > 90.0 or b = 90.0)")

    # Color entire residues by CA membership
    cmd.color("red",    "byres plddt_low_ca")
    cmd.color("yellow", "byres plddt_mid_ca")
    cmd.color("cyan",   "byres plddt_high_ca")
    cmd.color("blue",   "byres plddt_veryhigh_ca")

    # Print a quick summary
    n_low  = cmd.count_atoms("plddt_low_ca")
    n_mid  = cmd.count_atoms("plddt_mid_ca")
    n_high = cmd.count_atoms("plddt_high_ca")
    n_vhi  = cmd.count_atoms("plddt_veryhigh_ca")
    print(f"[pLDDT] CA counts in '{selection}': <50={n_low}, 50-70={n_mid}, 70-90={n_high}, >=90={n_vhi}")

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
