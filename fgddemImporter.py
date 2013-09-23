########################################################################
# fgddemImporter - A QGIS plugin
# Copyright (C) 2012 Minoru Akagri
# email : akaginch at gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import os

# initialize Qt resources from file resouces.py
import resources

plugin_classname = "fgddemImporter"

class fgddemImporter:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/fgddemImporter"

        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale")[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        # create action that will start plugin
        self.action = QAction(QIcon(":/plugins/fgddemImporter/icon.png"), self.tr("fgddem Importer"), self.iface.mainWindow())
        self.action.setWhatsThis(self.tr("fgddemImporter Plugin"))
        self.action.setStatusTip(self.tr("Import fgddem xml/zip files"))
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr("fgddem Importer"), self.action)

    def unload(self):
        # remove the plugin menu item and icon
        self.iface.removePluginMenu(self.tr("fgddem Importer"), self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        # create and show a configuration dialog or something similar
        d = fgddemDialog(self.iface)
        d.exec_()

    def tr(self, text):
        return QApplication.translate(plugin_classname, text, None, QApplication.UnicodeUTF8)

class fgddemDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.caption = self.tr("fgddem Importer")
        self.setupUi()
        s = QSettings()

    def setupUi(self):
        Dialog = self
        self.setObjectName("Dialog")
        self.resize(377, 100)
        self.setSizeGripEnabled(True)

        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")


        self.label1 = QLabel(Dialog)
        self.label1.setObjectName("label1")
        self.gridLayout.addWidget(self.label1, 0, 0, 1, 1)

        self.hboxlayout1 = QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.toolFile1 = QToolButton(Dialog)
        self.toolFile1.setObjectName("toolFile1")
        self.hboxlayout1.addWidget(self.toolFile1)

        self.toolClear = QToolButton(Dialog)
        self.toolClear.setObjectName("toolClear")
        self.hboxlayout1.addWidget(self.toolClear)

        self.gridLayout.addLayout(self.hboxlayout1, 0, 1, 1, 1, Qt.Alignment(Qt.AlignRight))

        self.inFiles = QListWidget(Dialog)
        self.inFiles.setObjectName("inFiles")
        self.inFiles.setAcceptDrops(True)
        self.gridLayout.addWidget(self.inFiles, 1, 0, 1, 2)

        self.label2 = QLabel(Dialog)
        self.label2.setObjectName("label2")
        self.gridLayout.addWidget(self.label2, 2, 0, 1, 1)

        self.label3 = QLabel(Dialog)
        self.label3.setObjectName("label3")
        self.gridLayout.addWidget(self.label3, 2, 1, 1, 1, Qt.Alignment(Qt.AlignRight))


        self.hboxlayout2 = QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.outDir = QLineEdit(Dialog)
#        self.outDir.setReadOnly(True)
        self.outDir.setObjectName("outDir")
        self.hboxlayout2.addWidget(self.outDir)

        self.toolDir1 = QToolButton(Dialog)
        self.toolDir1.setObjectName("toolDir1")
        self.hboxlayout2.addWidget(self.toolDir1)

        self.gridLayout.addLayout(self.hboxlayout2, 3, 0, 1, 2)

        self.check1 = QCheckBox(Dialog)
        self.check1.setObjectName("check1")
        self.gridLayout.addWidget(self.check1, 4, 0, 1, 2)

        self.check2 = QCheckBox(Dialog)
        self.check2.setObjectName("check2")
        self.gridLayout.addWidget(self.check2, 5, 0, 1, 2)

        self.buttonBox1 = QDialogButtonBox(self)
        self.buttonBox1.setOrientation(Qt.Horizontal)
        self.buttonBox1.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Close)
        self.buttonBox1.setObjectName("buttonBox1")
        self.gridLayout.addWidget(self.buttonBox1, 6, 0, 1, 2)

        self.setWindowTitle(self.tr("fgddem Importer"))
        self.label1.setText(self.tr("Files to import"))
        self.toolFile1.setText(self.tr("Add files"))
        self.toolClear.setText(self.tr("Clear"))
        self.label2.setText(self.tr("Output directory"))
        self.label3.setText("0" + self.tr(" files"))
        self.toolDir1.setText("...")
        self.check1.setText(self.tr("Replace nodata by zero"))
        self.check2.setText(self.tr("Converting only (run in background)"))

        self.importButton = self.buttonBox1.button(QDialogButtonBox.Ok)
        self.importButton.setEnabled(False)
        self.importButton.setText(self.tr("Import"))

        QObject.connect(self.toolFile1, SIGNAL("clicked()"), self.filedialog)
        QObject.connect(self.toolClear, SIGNAL("clicked()"), self.clear_files)
        QObject.connect(self.toolDir1, SIGNAL("clicked()"), self.directorydialog)
        QObject.connect(self.check2, SIGNAL("stateChanged(int)"), self.check2_changed)
        QObject.connect(self.buttonBox1, SIGNAL("accepted()"), self.import_fgddem)
        QObject.connect(self.buttonBox1, SIGNAL("rejected()"), self.close)

        QMetaObject.connectSlotsByName(Dialog)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        names = []
        for u in e.mimeData().urls():
            names.append(u.toLocalFile())
        self.add_files(names)

    def add_files(self, names):
        existing = []
        for i in range(self.inFiles.count()):
            existing.append(self.inFiles.item(i).text())

        allow_exts = ["zip", "xml"]
        for name in names:
            ext = QFileInfo(name).suffix()
            if not name in existing and ext.lower() in allow_exts:
                self.inFiles.addItem(name)
        self.label3.setText(self.tr("{0} files").format(self.inFiles.count()))
        self.importButton.setEnabled(True)
        if self.outDir.text() == "":
            self.outDir.setText(QFileInfo(names[0]).dir().path())

    def check2_changed(self, state):
        if state:
            self.importButton.setText(self.tr("Convert"))
        else:
            self.importButton.setText(self.tr("Import"))

    def directorydialog(self):
        file = QFileDialog.getExistingDirectory(self, self.tr("Select output directory"))
        if file != "":
            self.outDir.setText(file)

    def filedialog(self):
        names = QFileDialog.getOpenFileNames(self, self.tr("Select files to import"),
                                            QDir.homePath(), "JPGIS_GML files (*.zip *.xml)")
        if len(names) > 0:
            self.add_files(names)

    def clear_files(self):
        self.inFiles.clear()
        self.label3.setText(self.tr("{0} files").format(0))
        self.importButton.setEnabled(False)

    def import_fgddem(self):
        pdir = os.path.dirname(__file__)
        out_dir = self.outDir.text()
        if out_dir.find(" ") != -1:
            QMessageBox.warning(self, self.caption, self.tr("Error: Output directory cannot include any space characters."))
            return
        options = u"-out_dir %s " % out_dir

        if self.check1.isChecked():
            options += "-replace_nodata_by_zero "

        names = []
        for i in range(self.inFiles.count()):
            names.append(self.inFiles.item(i).text())

        cmd = u'python "%s/fgddem.py" %s' % (pdir, options + " ".join(map(quote_string, names)))
        #QMessageBox.information(self, "", cmd)

        msg = self.tr("Are you sure you want to start converting {0} files to GeoTIFF file?").format(len(names))
        if QMessageBox.question(self, self.caption, msg, QMessageBox.Ok | QMessageBox.Cancel) != QMessageBox.Ok:
            return

        self.importButton.setEnabled(False)
        if self.check2.isChecked():
            QgsRunProcess.create(cmd, False)
        else:
            os.system(cmd)
            paths = []
            for name in names:
                filetitle = QFileInfo(name).baseName()
                names.append(os.path.join(out_dir, filetitle + ".tif"))
            self.open_files(names)

    def open_files(self, names):
        colormap = [
            [-50, 0, 0, 205],
            [0, 0, 191, 191],
            [0.1, 57, 151, 105],
            [100, 117, 194, 93],
            [200, 230, 230, 128],
            [500, 202, 158, 75],
            [1000, 214, 187, 98],
            [2000, 185, 154, 100],
            [3000, 220, 220, 220],
            [3800, 255, 255, 255]]

        rampitems = []
        for item in colormap:
            rampitems.append(QgsColorRampShader.ColorRampItem(item[0], QColor(item[1], item[2], item[3])))

        for name in names:
            layer = QgsRasterLayer(name, QFileInfo(name).baseName())

            if hasattr(layer, "rasterShader"):
                # ver. < 2.0
                layer.setColorShadingAlgorithm(QgsRasterLayer.ColorRampShader)
                fcn = layer.rasterShader().rasterShaderFunction()
                fcn.setColorRampType(QgsColorRampShader.INTERPOLATED)
                fcn.setColorRampItemList(rampitems)
                layer.setDrawingStyle(QgsRasterLayer.SingleBandPseudoColor)
                QgsMapLayerRegistry.instance().addMapLayer(layer)
            else:
                # ver. >= 1.9 in developing
                QgsMapLayerRegistry.instance().addRasterLayer(layer)
                pass

    def close(self):
        QDialog.close(self)

def quote_string(s):
    return '"' + s + '"'

