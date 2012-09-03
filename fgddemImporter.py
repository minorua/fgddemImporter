from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import os
import zipfile
import shutil
import codecs
from xml.dom import minidom
import numpy

try:
    from osgeo import gdal
except ImportError:
    import gdal


# initialize Qt resources from file resouces.py
import resources

class fgddemImporter:
    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # create action that will start plugin
        self.action = QAction(QIcon(":/plugins/fgddemImporter/icon.png"), "fgddemImporter", self.iface.mainWindow())
        self.action.setWhatsThis("fgddemImporter Plugin")
        self.action.setStatusTip("Import fgddem xml/zip file")

        self.action2 = QAction(QIcon(":/plugins/fgddemImporter/icon.png"), "Settings", self.iface.mainWindow())
        self.action2.setWhatsThis("fgddemImporter Plugin Settings")
        self.action2.setStatusTip("Settings")

        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        QObject.connect(self.action2, SIGNAL("triggered()"), self.settings)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("fgddemImporter", self.action)     # & character is be able to use for menu title
        self.iface.addPluginToMenu("fgddemImporter", self.action2)

        s = QSettings()
        if s.value("fgddemImporter/colormaps_directory", '').toString() == '':
            for root, dirname, files in os.walk(os.path.join(os.getenv('OSGEO4W_ROOT'), 'apps/grass')):
                if root.find('colors') != -1:
                    s.setValue("fgddemImporter/colormaps_directory", root)
                    break

    def unload(self):
        # remove the plugin menu item and icon
        self.iface.removePluginMenu("fgddemImporter",self.action)
        self.iface.removePluginMenu("fgddemImporter",self.action2)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        # create and show a configuration dialog or something similar
        d = SelectColorDialog(self.iface)
        d.exec_()

    def settings(self):
        d = SettingsDialog(self.iface)
        d.exec_()

# Dialog
# REFFERED TO: fTools Plug-in

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class SelectColorDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.caption = self.tr("fgddemImporter")
        self.setupUi()

        s = QSettings()

    def setupUi(self):
        Dialog = self
        self.setObjectName(_fromUtf8("Dialog"))
        self.setWindowModality(Qt.WindowModal)
        self.resize(377, 100)
        self.setSizeGripEnabled(True)

        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.label1 = QLabel(Dialog)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.gridLayout.addWidget(self.label1, 0, 0, 1, 2)

        self.hboxlayout1 = QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.toolFile1 = QToolButton(Dialog)
        self.toolFile1.setObjectName(_fromUtf8("toolFile1"))
        self.hboxlayout1.addWidget(self.toolFile1)
        self.gridLayout.addLayout(self.hboxlayout1, 1, 0, 1, 2)

        self.inFiles = QListWidget(Dialog)
        self.inFiles.setObjectName(_fromUtf8("inFiles"))
        self.gridLayout.addWidget(self.inFiles, 2, 0, 1, 2)

        self.buttonBox1 = QDialogButtonBox(self)
        self.buttonBox1.setOrientation(Qt.Horizontal)
        self.buttonBox1.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Close)
        self.buttonBox1.setObjectName(_fromUtf8("buttonBox1"))
        self.gridLayout.addWidget(self.buttonBox1, 3, 1, 1, 1)

        self.setWindowTitle(QApplication.translate("Dialog", "fgddemImporter", None, QApplication.UnicodeUTF8))
        self.label1.setText(QApplication.translate("Dialog", "Color : choose a color map for the raster layer.", None, QApplication.UnicodeUTF8))
        self.toolFile1.setText(QApplication.translate("Dialog", "Add", None, QApplication.UnicodeUTF8))


        QObject.connect(self.toolFile1, SIGNAL("clicked()"), self.filedialog)
        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("accepted()")), self.accept)
        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("rejected()")), self.close)

#        self.buttonBox1.acceptDrops = True
#        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("dragEnter()")), self.dragenter)

        QMetaObject.connectSlotsByName(Dialog)

    def fgddemImporter(self, name):
        return 0

    def dragenter(self):
        QMessageBox.information(self, self.caption, 'dragenter')


    def filedialog(self):
        names = map(str, QFileDialog.getOpenFileNames(self, "Select files to import", QDir.homePath(), _fromUtf8("JPGIS GML (*.zip *.xml)")))
        
        if len(names) > 0:
            existing = []
            for i in range(self.inFiles.count()):
                existing.append(str(self.inFiles.item(i).text()))

            for name in names:
                if not name in existing:
                    self.inFiles.addItem(name)


    def dummy(self):
        dialog = QFileDialog(self)
        dialog.setDirectory(QDir.homePath())
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter(_fromUtf8("JPGIS GML (*.zip *.xml)"))
        if dialog.exec_():
            fileNames = map(str, dialog.selectedFiles())

            QMessageBox.information(self, self.caption, ' '.join(fileNames))
            


    def status(self, str):
        self.label1.setText(str)

    def accept(self):
        names = []
        for i in range(self.inFiles.count()):
            names.append(str(self.inFiles.item(i).text()))

        fgddem_main(names,status=self.status)
        
        for name in names:
            root, ext = os.path.splitext(name)
            head, tail = os.path.split(name)
            filetitle, dummy = os.path.splitext(tail)
            layer = QgsRasterLayer(root + '.tif', filetitle)
            QgsMapLayerRegistry.instance().addMapLayer(layer)

    def close(self):
        s = QSettings()
 #       s.setValue("fgddemImporter/lastcolor", self.color_name)
        QDialog.close(self)


class SettingsDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.caption = self.tr("Settings - fgddemImporter")
        self.setupUi()
        
        s = QSettings()
        self.colorsDir.setText(str(s.value("fgddemImporter/colormaps_directory", '').toString()))
        self.setWindowTitle(self.caption)

    def setupUi(self):
        Dialog = self
        self.setObjectName(_fromUtf8("Dialog"))
        self.setWindowModality(Qt.WindowModal)
        self.resize(377, 100)
        self.setSizeGripEnabled(True)

        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.label1 = QLabel(Dialog)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.gridLayout.addWidget(self.label1, 0, 0, 1, 2)

        self.hboxlayout1 = QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.colorsDir = QLineEdit(Dialog)
        self.colorsDir.setReadOnly(True)
        self.colorsDir.setObjectName(_fromUtf8("colorsDir"))
        self.hboxlayout1.addWidget(self.colorsDir)
        self.toolFile1 = QToolButton(Dialog)
        self.toolFile1.setObjectName(_fromUtf8("toolFile1"))
        self.toolFile1.setText("...")
        self.hboxlayout1.addWidget(self.toolFile1)
        self.gridLayout.addLayout(self.hboxlayout1, 1, 0, 1, 2)

        self.buttonBox1 = QDialogButtonBox(self)
        self.buttonBox1.setOrientation(Qt.Horizontal)
        self.buttonBox1.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttonBox1.setObjectName(_fromUtf8("buttonBox1"))
        self.gridLayout.addWidget(self.buttonBox1, 2, 1, 1, 1)

        self.setWindowTitle(QApplication.translate("Dialog", "Settings - fgddemImporter", None, QApplication.UnicodeUTF8))
        self.label1.setText(QApplication.translate("Dialog", "Colormaps directory", None, QApplication.UnicodeUTF8))

        QObject.connect(self.toolFile1, SIGNAL("clicked()"), self.colormaps_directory)
        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("accepted()")), self.accept)
        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("rejected()")), self.close)

        QMetaObject.connectSlotsByName(Dialog)

    def colormaps_directory(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file != '':
            self.colorsDir.setText(file)

    def accept(self):
        s = QSettings()
        s.setValue("fgddemImporter/colormaps_directory", self.colorsDir.text())
        self.close()


def fgddem_main(filenames, out_dir = '', replace_nodata_by_zero = 0, status = None, progress = None):
    global verbose, quiet, debug_mode
    verbose = 0
    quiet = 0
    debug_mode = 0

    import fgddem
    format = 'GTiff'

    gdal_merge_options = ''
    gdalwarp_options = ''
    gdal_merge_ext = ''
    if os.name != 'nt':     # nt: windows
        gdal_merge_ext = '.py'

    gdal_version = int(gdal.VersionInfo())
    gdal.AllRegister()

    if quiet:
        gdal_merge_options += ' -q'
    if verbose == 0:
        gdalwarp_options += ' -q'

    if out_dir != '' and os.path.exists(out_dir) == False:
        os.mkdir(out_dir)
        if verbose:
            print '"%s" directory has been created.' % out_dir

    if replace_nodata_by_zero == 0:
        gdal_merge_options += ' -a_nodata -9999'
        gdalwarp_options += ' -dstnodata -9999'

    driver = gdal.GetDriverByName(format)
    if driver is None:
        print 'Format driver %s not found.' % format
        return 0

    fi_processed = 0
    for src_file in filenames:
        if quiet == 0 and len(filenames) > 1:
            if status is not None:
                status('Processing files ( %d / %d )' % (fi_processed+1, len(filenames)))

        if out_dir == '':
            src_root, ext = os.path.splitext(src_file)
            dst_root = src_root
        else:
            bn = os.path.basename(src_file)
            filetitle, ext = os.path.splitext(bn)
            dst_root = os.path.join(out_dir,filetitle)

        dst_file = dst_root + '.tif'

        ext = ext.lower()
        if ext == '.zip':
            if quiet == 0:
                status('extracting %s' % src_file)
            fgddem.unzip(src_file,dst_root)

            if quiet == 0:
                status('translating %s' % dst_root)

            if quiet == 0 and verbose == 0:
                if progress is not None: progress(0.0)

            fi_processed_in = 0
            file_list = os.listdir(dst_root)

            filelist_file = os.path.join(dst_root,'filelist.txt')
            f = open(filelist_file,'w')

            for file_in in file_list:
                file_in = os.path.join(dst_root,file_in)
                if file_in.find('meta') == -1:
                    fgddem.convert_jpgis_gml(file_in,file_in+'.tif',driver,[],replace_nodata_by_zero)
                    f.write(file_in+'.tif\n')

                fi_processed_in += 1
                if quiet == 0 and verbose == 0:
                    if progress is not None: progress(fi_processed_in / float(len(file_list)))

            f.close()

            if gdal_version >= 1900:
                merge_command = 'gdal_merge' + gdal_merge_ext + gdal_merge_options + ' -o ' + dst_file + ' --optfile ' + filelist_file
                # TODO: testing in Linux
                # Wildcards cannot be used for arguments now. See http://trac.osgeo.org/gdal/ticket/4542 (2012/04/08)
            else:
                merge_command = 'gdalwarp' + gdalwarp_options + ' ' + os.path.join(dst_root,'*.tif') + ' ' + dst_file

            if quiet == 0:
                print 'merging files'
            if verbose:
                print 'executing %s' % merge_command
            os.system(merge_command)

            if quiet == 0:
                print 'removing temporary files'
                print ''
            shutil.rmtree(dst_root)

        elif ext == '.xml' and src_file.find('meta') == -1:
            fgddem.convert_jpgis_gml(src_file,dst_file,driver,[],replace_nodata_by_zero)

        fi_processed += 1

    if quiet == 0:
        status('completed')

    return 0

