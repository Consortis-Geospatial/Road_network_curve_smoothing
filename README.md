#  Road Network Curve Smoothing (QGIS Plugin)

## Overview

**Road Network Curve Smoothing** is a QGIS plugin that detects curve points (bends) on a road network within a selected polygon boundary, based on a user-defined angle range.
It creates an output  temporary **point layer** of detected curve locations with their corresponding angles, which you can then inspect, symbolize, or use in further analysis.

---

## Features

- Select **one polygon** as a boundary (e.g. study area, neighborhood, district).
- Select a **line layer** representing the road network.
- Specify a **minimum and maximum angle** (in degrees) to control which curves are detected.
- Automatically creates a **memory point layer** with:
  - `id` – sequential ID of each detected curve
  - `angle` – calculated angle (in degrees) at that curve
- Works with both **single-part** and **multi-part** line geometries.
- Ignores vertices outside the selected polygon (uses a small inward buffer to avoid boundary issues).

---

## How It Works

1. You select exactly **one polygon feature** from the chosen polygon layer.
2. The plugin builds a slightly **shrunk inner boundary** from that polygon using a small negative buffer.
3. For each road segment (line geometry):
   - It reads the vertices in order.
   - For every triplet of points (p1–p2–p3), it calculates the angle at `p2`.
4. Angles that fall within your specified **[Min, Max]** range and lie within the inner boundary polygon are flagged as curve points.
5. All detected curve points are exported as a **temporary point layer** and added to the current QGIS project.

> **Note:** The angle is calculated using basic vector math (dot product and magnitudes) and converted to degrees (0°–180°).

---

## Requirements

- QGIS (3.x)
- PyQt5 / QGIS Python environment (default in QGIS)
- The plugin uses:
  - `qgis.core`  
  - `qgis.PyQt`  
  - `qgis.utils.iface`  

No external Python packages are required beyond QGIS’ own libraries.

---

## Installation

1. Clone or download this repository.
''' bash 
git clone https://github.com/Consortis-Geospatial/Road_network_curve_smoothing.git 
'''
2. Copy the plugin folder (the folder containing `__init__.py`, the main plugin file, `metadata.txt`, `curve.png`, etc.) into your QGIS plugin directory:

   - **Windows:**  
     `C:\Users\<YourUser>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux:**  
     `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS:**  
     `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

   (Adjust the profile name if you use a non-default profile.)

3. Restart QGIS.
4. Go to **Plugins → Manage and Install Plugins…**
5. In the **Installed** tab, find **Road Network Curve Smoothing** and check it to enable.         

---

## Usage

1. **Prepare Your Data**
   - Add your **polygon layer** (e.g. area boundary).
   - Add your **road network line layer**.

2. **Select a Polygon**
   - Use the **Select Features** tool to select **exactly one** polygon in the polygon layer.
   - The plugin requires a single selected polygon as the analysis boundary.

3. **Run the Plugin**
   - In the QGIS menu, go to  
     **Plugins → Road Network Curve Smoothing**  
     or click the toolbar icon ![curve icon](curve.png) if visible.
   - The plugin dialog will appear.

4. **Set Parameters**
   - **Polygon Layer (Boundary):** choose your polygon layer.
   - **Line Layer (Roads):** choose your road network layer.
   - **Angle Range (degrees):**
     - *Min:* default = 45°
     - *Max:* default = 75°
   - Click **Run**.

5. **Results**
   - If suitable curve points are found:
     - A new memory layer named **`Detected_Curves`** is added to your Layers panel.
     - It contains a point at each detected curve with:
       - `id`: unique integer
       - `angle`: angle in degrees (rounded to 2 decimal places)
   - If **no curves** are found within the specified range, an info message appears in the QGIS message bar.

---

## Dialog Description

The main dialog includes:

- **Polygon Layer (Boundary)**  
  Drop-down to choose the polygon layer used as boundary.

- **Line Layer (Roads)**  
  Drop-down to choose the road network line layer.

- **Angle Range (degrees)**  
  - `Min` and `Max` values using double spin boxes from 0 to 180°.
  - Defaults to 45°–75°.

- **Run Button**  
  Starts the processing using the selected layers and angle range.

---

## Messages & Error Handling

The plugin uses the QGIS message bar (`iface.messageBar()`) to show feedback:

- **Warning:**  
  - If polygon or line layer is not selected.  
  - If the number of selected polygons is not exactly one.
- **Info:**  
  - If no curve points were found in the given angle range.
- **Success:**  
  - Shows how many curve points were exported and the angle range used.

---

## Limitations & Notes

- The plugin currently supports:
  - Polygon boundary layers.
  - Line layers (roads) with polyline geometries (single or multi-part).
- The **inner boundary** uses a fixed small negative buffer (`tolerance = 0.0001`).  
  If your data uses very large or very small coordinate values, you may want to adjust this value in the code.
- The output is a **memory layer**; if you want to keep it permanently, right-click it and choose:
  - **Export → Save Features As…**

---

## Code Structure

- `RoadNetworkCurveSmoothingDialog`  
  - Builds the user interface (layer selections, angle inputs, run button).

- `RoadNetworkCurveSmoothing`  
  - Handles plugin initialization (`initGui`, `unload`).
  - Shows the dialog (`run`).
  - Processes the selected layers and generates the output layer (`process`).
  - Calculates angles between three points (`calculate_angle`).

---

## License
This plugin is released under the GPL-3.0 license.

---

## Support and Contribution
- **Homepage**: [https://github.com/Consortis-Geospatial],(https://github.com/Consortis-Geospatial)
- **Author**: Dimitra Pappa -Consortis Geospatial
- **email**: pappa@consortis.gr
- **Repository**: [https://github.com/Consortis-Geospatial/Road_network_curve_smoothing],(https://github.com/Consortis-Geospatial/Road_network_curve_smoothing)
- **Issues Tracker**: [https://github.com/Consortis-Geospatial/Road_network_curve_smoothing],(https://github.com/Consortis-Geospatial/Road_network_curve_smoothing)

