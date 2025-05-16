# Structure Analysis Project

This project provides tools to define and analyze 2D structural elements, such as bars and nodes, with detailed mechanical properties and loading capabilities. It also includes a GUI interface for interactive visualization and design.

## 🏗️ Project Structure

- **Structure_Analysis** – Core mechanics for node, bar and structure modeling.
- **Structure_AnalysisGUI** – Graphical interface for building and analyzing structures.
- **utils** – Helper modules for calculations, material properties, and possibly data input/output handling.

## 📦 Features

- Define 2D structural bars with rectangular or circular cross-sections.
- Support for solid and hollow sections.
- Assign mechanical properties like material, thickness, and loads.
- Perform geometric and mechanical analysis:
  - Volume
  - Mass
  - Sectional area
  - Moment of inertia
  - Static moment
  - Von Mises stress check for resistance analysis
- Consistency checks (e.g. node overlap, bar length validation).
- Modular design allows defining multiple bars and combining them into structures.
- GUI for visual and interactive structure creation (in `Structure_AnalysisGUI`).

## 🔧 Example Usage

```python
from Structure_Analysis import Node, Bar, Structure

# Create nodes
start = Node("A", 0, 0)
end = Node("B", 0, 1000)

# Create a bar
bar = Bar(length=1000, width=100, height=200, hollow=False, section='rectangular', material='steel', alpha=90, start_node=start, end_node=end)
bar.add_load(position=500, fx=0, fy=-1000, m=0)

# Create a structure and add the bar
frame = Structure(name="Simple Frame")
frame.add_bar(bar)

# Print structure info
frame.info()
```

## 🧪 Requirements

- Python 3.7+
- NumPy
- SciPy
- Matplotlib
- pandas
- tkinter

Install dependencies:

```bash
pip install numpy scipy matplotlib pandas tkinter
```

## 🧠 Concepts Covered

- Structural mechanics basics (axial force, shear, bending moment)
- Material strength and yield checks
- Geometry calculations and transformations

## 📁 Directory Overview

```
project_root/
├── Structure_Analysis.py
├── Structure_AnalysisGUI.py
├── utils
└── README.md
```

## ✍️ Author

- Developed by Paolo Susini - Centro di Ricerca E. Piaggio Pisa -  
