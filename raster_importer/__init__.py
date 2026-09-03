def classFactory(iface):
    """Lädt die Plugin-Klasse für QGIS."""
    from .plugin import RasterImporterPlugin
    return RasterImporterPlugin(iface)
