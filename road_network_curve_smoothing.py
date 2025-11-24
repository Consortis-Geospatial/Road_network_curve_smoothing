from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QAction, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QDoubleSpinBox, QHBoxLayout
)
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsFeature,
    QgsPointXY,
    QgsVectorLayer,
    QgsField,
    QgsWkbTypes
)
from qgis.utils import iface
from PyQt5.QtCore import QVariant
import os
import math


class RoadNetworkCurveSmoothingDialog(QDialog):
    """Dialog for selecting layers and angle range"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Road Network Curve Smoothing")
        self.setMinimumWidth(320)

        layout = QVBoxLayout()

        # --- Polygon layer selection ---
        self.poly_label = QLabel("Select Polygon Layer (Boundary):")
        self.poly_combo = QComboBox()

        # --- Line layer selection ---
        self.line_label = QLabel("Select Line Layer (Roads):")
        self.line_combo = QComboBox()

        # Populate combos with layers
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == layer.VectorLayer:
                if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    self.poly_combo.addItem(layer.name(), layer)
                elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                    self.line_combo.addItem(layer.name(), layer)

        # --- Angle range selection ---
        self.angle_label = QLabel("Angle Range (degrees):")
        angle_layout = QHBoxLayout()

        self.min_angle_spin = QDoubleSpinBox()
        self.min_angle_spin.setRange(0, 180)
        self.min_angle_spin.setValue(45)
        self.min_angle_spin.setSuffix("°")

        self.max_angle_spin = QDoubleSpinBox()
        self.max_angle_spin.setRange(0, 180)
        self.max_angle_spin.setValue(75)
        self.max_angle_spin.setSuffix("°")

        angle_layout.addWidget(QLabel("Min:"))
        angle_layout.addWidget(self.min_angle_spin)
        angle_layout.addWidget(QLabel("Max:"))
        angle_layout.addWidget(self.max_angle_spin)

        # --- OK button ---
        self.ok_button = QPushButton("Run")
        self.ok_button.setDefault(True)

        # --- Layout assembly ---
        layout.addWidget(self.poly_label)
        layout.addWidget(self.poly_combo)
        layout.addWidget(self.line_label)
        layout.addWidget(self.line_combo)
        layout.addWidget(self.angle_label)
        layout.addLayout(angle_layout)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def getLayers(self):
        poly_layer = self.poly_combo.currentData()
        line_layer = self.line_combo.currentData()
        return poly_layer, line_layer

    def getAngleRange(self):
        return self.min_angle_spin.value(), self.max_angle_spin.value()


class RoadNetworkCurveSmoothing:
    """Main plugin class"""

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None

    def initGui(self):
        """Add toolbar button and menu item"""
        icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "curve.png")
        self.action = QAction(QIcon(icon_path), "Road Network Curve Smoothing", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Road Network Curve Smoothing", self.action)

    def unload(self):
        """Remove toolbar button and menu item"""
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("&Road Network Curve Smoothing", self.action)

    def run(self):
        """Show the dialog"""
        dialog = RoadNetworkCurveSmoothingDialog()
        dialog.ok_button.clicked.connect(lambda: self.process(dialog))
        dialog.exec_()

    def calculate_angle(self, p1, p2, p3):
        """Calculate angle in degrees between three points (p1-p2-p3)."""
        a = (p1.x() - p2.x(), p1.y() - p2.y())
        b = (p3.x() - p2.x(), p3.y() - p2.y())
        dot = a[0]*b[0] + a[1]*b[1]
        mag_a = math.sqrt(a[0]**2 + a[1]**2)
        mag_b = math.sqrt(b[0]**2 + b[1]**2)
        if mag_a == 0 or mag_b == 0:
            return 180
        cos_theta = dot / (mag_a * mag_b)
        cos_theta = max(min(cos_theta, 1), -1)
        return math.degrees(math.acos(cos_theta))

    def process(self, dialog):
        """Detect sharp turns within selected boundary polygon"""
        poly_layer, line_layer = dialog.getLayers()
        if not poly_layer or not line_layer:
            self.iface.messageBar().pushWarning("Road Network Curve Smoothing", "Please select both layers.")
            return

        selected_polys = poly_layer.selectedFeatures()
        if len(selected_polys) != 1:
            self.iface.messageBar().pushWarning("Road Network Curve Smoothing", "Please select exactly one polygon feature.")
            return

        boundary_geom = selected_polys[0].geometry()
        tolerance = 0.0001
        inner_boundary = boundary_geom.buffer(-tolerance, 1)

        min_angle, max_angle = dialog.getAngleRange()
        sharp_turns = []

        for feat in line_layer.getFeatures():
            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                continue

            if geom.isMultipart():
                parts = geom.asMultiPolyline()
            else:
                parts = [geom.asPolyline()]

            for part in parts:
                if len(part) < 3:
                    continue

                for i in range(1, len(part) - 1):
                    angle = self.calculate_angle(part[i - 1], part[i], part[i + 1])
                    if min_angle <= angle <= max_angle:
                        pt_geom = QgsGeometry.fromPointXY(part[i])
                        if pt_geom.within(inner_boundary):
                            sharp_turns.append((pt_geom, angle))

        if not sharp_turns:
            self.iface.messageBar().pushInfo("Road Network Curve Smoothing", "No curves found within the selected range.")
            dialog.close()
            return

        # --- Export results ---
        crs = line_layer.crs().authid()
        result_layer = QgsVectorLayer(f"Point?crs={crs}", "Detected_Curves", "memory")
        prov = result_layer.dataProvider()
        prov.addAttributes([QgsField("id", QVariant.Int), QgsField("angle", QVariant.Double)])
        result_layer.updateFields()

        new_feats = []
        for i, (pt_geom, angle) in enumerate(sharp_turns):
            new_feat = QgsFeature(result_layer.fields())
            new_feat.setGeometry(pt_geom)
            new_feat.setAttribute("id", i + 1)
            new_feat.setAttribute("angle", round(angle, 2))
            new_feats.append(new_feat)

        prov.addFeatures(new_feats)
        result_layer.updateExtents()
        QgsProject.instance().addMapLayer(result_layer)

        self.iface.messageBar().pushSuccess(
            "Road Network Curve Smoothing",
            f"Exported {len(new_feats)} curve point(s) within {min_angle:.1f}°–{max_angle:.1f}° range."
        )
        dialog.close()
