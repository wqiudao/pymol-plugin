
Method A (Recommended, Easiest)

Open PyMOL

Go to the menu:
Plugin → Plugin Manager → Install New Plugin

In the dialog window:

Set Install from to URL

Paste the GitHub raw file URL of the plugin
```
https://github.com/wqiudao/pymol-plugin/blob/main/plddt_coloring_plugin.py
```
Click Install

Restart PyMOL (recommended)









# PyMolTint
PyMolTint is a PyMOL plugin designed to enhance the visualization of molecular structures by allowing users to easily highlight specific residues with color and markers. This tool simplifies the process of marking residues with colored spheres, helping to emphasize important areas in a molecular structure for better analysis and presentation.
1. **af2color:** set colors for atoms in the loaded PDB file based on the atom_plddts values from the JSON file.
```
af2color json_file
```
2. **show_residue_sphere:**  adds a colored sphere at the position of a specified residue in the loaded structure.
```
show_residue_sphere 666

show_residue_sphere 6,6

show_residue_sphere 888,8,1 0.5 0.1

# show_residue_sphere residue_number, sph_radius, sph_color(space-separated RGB string)
```
# install
Download the *PyMolTint.py* script to your local machine, Launch PyMOL, and use the following command to load the *PyMolTint.py* script into PyMOL
```
run /path/to/PyMolTint.py
```
![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/loading_plugin.png)

## 1. af2color

Set colors for atoms in the loaded PDB file based on the atom_plddts values from the JSON file.
Parameters:
- `json_file`: Path to the JSON file containing the atom_plddts values

The JSON file is located in PyMOL's current working directory; otherwise, the full path is required.

<pre> af2color json_file  </pre>

### 1. af2color: Data Preparation
-
  We need to prepare two files, located in the same directory. 
  1. The Alphafold prediction result files, including `PDB` or `CIF` format structure files, as well as the corresponding `JSON` format files containing pLDDT values (The predicted local distance difference test).
  2. Structural predictions can be obtained through Alphafold3 online (https://golgi.sandbox.google.com/), which is very fast, but currently limited to 20 predictions per day. Alternatively, you can download from the Alphafold database, if available.
  ![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/AF2Color/af2color0.png)
  
  ![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/AF2Color/af2color_data.png)

-
 
### 1. af2color: run (Color structures)

<pre> af2color fold_5xwp_full_data_0.json  </pre>
-
 ![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/AF2Color/af2color1.png)
 ![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/AF2Color/af2color2.png)
-
<img src="https://github.com/wqiudao/PyMolTint/blob/main/imgs/AF2Color/af2color_legend.png" alt="Alt text" width="300">
-

## 2. show_residue_sphere
show_residue_sphere, which adds a colored sphere at the position of a specified residue in the loaded structure. 

[Color Values](https://pymolwiki.org/index.php/Color_Values) 
<pre>Input Parameters:
	residue_number: The residue number to mark with a sphere. Defaults to 1.
	sph_radius: The radius of the sphere. Defaults to 2.
	sph_color: The color of the sphere, provided as a space-separated RGB string (e.g., '1.0 0.0 0.0' for red).
</pre>
```
show_residue_sphere 666
```
![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/show_residue_sphere/show_residue_sphere1.png)
```
show_residue_sphere 6,6
```
![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/show_residue_sphere/show_residue_sphere2.png)
 ```
show_residue_sphere 888,8,1 0.5 0.1
```
![PyMolTint.py](https://github.com/wqiudao/PyMolTint/blob/main/imgs/show_residue_sphere/show_residue_sphere3.png)




```
cd /path/to/my/cifs/
 
 
obj = cmd.get_names()[0]  # e.g. 'scas_283_model'

 
prefix = obj.replace("_model", "")

 
cmd.save(f"{prefix}_protein.pdb", "chain A")
cmd.save(f"{prefix}_rna.pdb", "chain B")




```
 




# References/Citations
DeLano, W. L. (2002). Pymol: An open-source molecular graphics tool. CCP4 Newsl. Protein Crystallogr, 40(1), 82-92.
