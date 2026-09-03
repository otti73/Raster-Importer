import os
import tempfile
import time
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsRasterLayer, QgsProject, Qgis
from osgeo import gdal
from .dialog import RasterImporterDialog

class RasterImporterPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dialog = None

    def tr(self, message):
        return QCoreApplication.translate('RasterImporterPlugin', message)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.svg')
        self.action = QAction(
            QIcon(icon_path),
            self.tr('Raster Importer'),
            self.iface.mainWindow()
        )
        self.action.setStatusTip(self.tr('Importiert Rasterdateien sauber in QGIS'))
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr('&Raster Importer'), self.action)

    def unload(self):
        self.iface.removePluginMenu(self.tr('&Raster Importer'), self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dialog = RasterImporterDialog(self.iface.mainWindow())

        result = self.dialog.exec() if hasattr(self.dialog, 'exec') else self.dialog.exec_()
        
        if not result:
            return

        file_path = self.dialog.get_selected_file()
        if not file_path or not os.path.exists(file_path):
            self.iface.messageBar().pushMessage(
                self.tr("Fehler"),
                self.tr("Bitte wähle eine gültige Rasterdatei aus."),
                level=Qgis.Warning,
                duration=4
            )
            return

        layer_name = os.path.splitext(os.path.basename(file_path))[0]

        if self.dialog.should_fit_to_view():
            canvas = self.iface.mapCanvas()
            extent = canvas.extent()
            crs = canvas.mapSettings().destinationCrs().authid()

            if extent.isEmpty() or not crs:
                self.iface.messageBar().pushMessage(
                    self.tr("Warnung"),
                    self.tr("Kartenausschnitt konnte nicht bestimmt werden. Laden ohne Einpassung."),
                    level=Qgis.Warning,
                    duration=4
                )
                layer_to_load = file_path
            else:
                xmin, ymin, xmax, ymax = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
                timestamp = int(time.time())
                temp_vrt = os.path.join(tempfile.gettempdir(), f"{layer_name}_{timestamp}.vrt")
                
                options = gdal.TranslateOptions(
                    outputSRS=crs,
                    outputBounds=[xmin, ymax, xmax, ymin]
                )
                
                try:
                    gdal.Translate(temp_vrt, file_path, options=options)
                    layer_to_load = temp_vrt
                except Exception as e:
                    self.iface.messageBar().pushMessage(
                        self.tr("GDAL Fehler"),
                        self.tr(f"Fehler beim Erstellen der VRT: {e}"),
                        level=Qgis.Critical,
                        duration=5
                    )
                    layer_to_load = file_path
        else:
            layer_to_load = file_path

        layer = QgsRasterLayer(layer_to_load, layer_name)
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self.iface.messageBar().pushMessage(
                self.tr("Erfolg"),
                self.tr(f"Raster '{layer_name}' erfolgreich hinzugefügt."),
                level=Qgis.Success,
                duration=3
            )
        else:
            self.iface.messageBar().pushMessage(
                self.tr("Fehler"),
                self.tr("Die Datei konnte nicht als gültiger Rasterlayer geladen werden."),
                level=Qgis.Critical,
                duration=5
            )
