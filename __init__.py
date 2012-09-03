def name():
    return "fgddemImporter"

def description():
    return "Import fgddem xml/zip file."

def category():
  return "Raster"

def version():
    return "Version Beta 2012/06/06"

def qgisMinimumVersion():
    return "1.0"

def authorName():
    return "anonymous"

def classFactory(iface):
    import fgddemImporter
    return fgddemImporter.fgddemImporter(iface)

