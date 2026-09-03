import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox, 
    QDialogButtonBox, QGroupBox, QFormLayout
)
from qgis.gui import QgsFileWidget

class RasterImporterDialog(QDialog):
    def __init__(self, parent=None):
        super(RasterImporterDialog, self).__init__(parent)
        self.setWindowTitle(self.tr("Raster Importer v1.5.2"))
        self.resize(500, 220)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        group_box = QGroupBox(self.tr("Rasterdatei auswählen"))
        group_layout = QFormLayout()
        group_layout.setContentsMargins(10, 15, 10, 15)

        self.file_widget = QgsFileWidget()
        self.file_widget.setDialogTitle(self.tr("Rasterdatei auswählen"))
        self.file_widget.setFilter("Rasterdaten (*.tif *.tiff *.asc *.img *.png *.jpg *.jpeg);;Alle Dateien (*)")
        
        # Abfangen von StorageMode Unterschieden zwischen PyQt5/PyQt6
        if hasattr(QgsFileWidget, 'GetFile'):
            self.file_widget.setStorageMode(QgsFileWidget.GetFile)
        elif hasattr(QgsFileWidget, 'StorageMode'):
            self.file_widget.setStorageMode(QgsFileWidget.StorageMode.GetFile)

        group_layout.addRow(QLabel(self.tr("Datei:")), self.file_widget)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        self.extent_checkbox = QCheckBox(self.tr("Im aktuellen Kartenausschnitt platzieren (Georeferenzieren via VRT)"))
        self.extent_checkbox.setChecked(True)
        self.extent_checkbox.setToolTip(
            self.tr("Erstellt eine temporäre VRT-Datei, die das Raster exakt über das aktuelle Kartenfenster spannt.")
        )
        layout.addWidget(self.extent_checkbox)

        # Kompatibilitäts-Check für QDialogButtonBox Enums (PyQt5 vs PyQt6)
        if hasattr(QDialogButtonBox, 'StandardButton'):
            ok_btn = QDialogButtonBox.StandardButton.Ok
            cancel_btn = QDialogButtonBox.StandardButton.Cancel
        else:
            ok_btn = QDialogButtonBox.Ok
            cancel_btn = QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(ok_btn | cancel_btn)
        self.button_box.button(ok_btn).setText(self.tr("Raster Laden"))
        self.button_box.button(cancel_btn).setText(self.tr("Abbrechen"))
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_selected_file(self):
        return self.file_widget.filePath().strip()

    def should_fit_to_view(self):
        return self.extent_checkbox.isChecked()
