########################################################################
# Raster Painter - A QGIS plugin
# Copyright (C) 2012 Akagri Minoru
# email : akaginch@yahoo.co.jp
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################
# version beta 2012/06/09
# not support filepath with multibyte string

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import os

# initialize Qt resources from file resouces.py
import resources

plugin_title = "fgddem Importer"
plugin_classname = "fgddemImporter"

def getPluginDir():
    d = os.getenv('HOME') + '/.qgis/python/plugins/' + plugin_classname
    if os.path.exists(d): return d
    qgis_prefix = unicode(QgsApplication.prefixPath())
    d = qgis_prefix + '/python/plugins/' + plugin_classname
    if os.path.exists(d): return d
    d = qgis_prefix + '/share/qgis/python/plugins/' + plugin_classname
    if os.path.exists(d): return d
    return None

class fgddemImporter:
    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # create action that will start plugin
        self.action = QAction(QIcon(":/plugins/fgddemImporter/icon.png"), plugin_title, self.iface.mainWindow())
        self.action.setWhatsThis("fgddemImporter Plugin")
        self.action.setStatusTip("Import fgddem xml/zip files")
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(plugin_title, self.action)

    def unload(self):
        # remove the plugin menu item and icon
        self.iface.removePluginMenu(plugin_title, self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        # create and show a configuration dialog or something similar
        d = fgddemDialog(self.iface)
        d.exec_()

# Dialog
# REFFERED TO: fTools Plug-in

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class fgddemDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.caption = self.tr(plugin_title)
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
        self.gridLayout.addWidget(self.label1, 0, 0, 1, 1)

        self.hboxlayout1 = QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))

        self.toolFile1 = QToolButton(Dialog)
        self.toolFile1.setObjectName(_fromUtf8("toolFile1"))
        self.hboxlayout1.addWidget(self.toolFile1)

        self.toolClear = QToolButton(Dialog)
        self.toolClear.setObjectName(_fromUtf8("toolClear"))
        self.hboxlayout1.addWidget(self.toolClear)

        self.gridLayout.addLayout(self.hboxlayout1, 0, 1, 1, 1, Qt.Alignment(Qt.AlignRight))

        self.inFiles = QListWidget(Dialog)
        self.inFiles.setObjectName(_fromUtf8("inFiles"))
        self.gridLayout.addWidget(self.inFiles, 1, 0, 1, 2)

        self.label2 = QLabel(Dialog)
        self.label2.setObjectName(_fromUtf8("label2"))
        self.gridLayout.addWidget(self.label2, 2, 0, 1, 1)

        self.label3 = QLabel(Dialog)
        self.label3.setObjectName(_fromUtf8("label3"))
        self.gridLayout.addWidget(self.label3, 2, 1, 1, 1, Qt.Alignment(Qt.AlignRight))


        self.hboxlayout2 = QHBoxLayout()
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))

        self.outDir = QLineEdit(Dialog)
#        self.outDir.setReadOnly(True)
        self.outDir.setObjectName(_fromUtf8("outDir"))
        self.hboxlayout2.addWidget(self.outDir)

        self.toolDir1 = QToolButton(Dialog)
        self.toolDir1.setObjectName(_fromUtf8("toolDir1"))
        self.hboxlayout2.addWidget(self.toolDir1)

        self.gridLayout.addLayout(self.hboxlayout2, 3, 0, 1, 2)

        self.check1 = QCheckBox(Dialog)
        self.check1.setObjectName(_fromUtf8("check1"))
        self.gridLayout.addWidget(self.check1, 4, 0, 1, 2)

        self.check2 = QCheckBox(Dialog)
        self.check2.setObjectName(_fromUtf8("check2"))
        self.gridLayout.addWidget(self.check2, 5, 0, 1, 2)

        self.buttonBox1 = QDialogButtonBox(self)
        self.buttonBox1.setOrientation(Qt.Horizontal)
        self.buttonBox1.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Close)
        self.buttonBox1.setObjectName(_fromUtf8("buttonBox1"))
        self.gridLayout.addWidget(self.buttonBox1, 6, 0, 1, 2)

        self.setWindowTitle(QApplication.translate(plugin_classname, plugin_title, None, QApplication.UnicodeUTF8))
        self.label1.setText(QApplication.translate(plugin_classname, "Files to import", None, QApplication.UnicodeUTF8))
        self.toolFile1.setText(QApplication.translate(plugin_classname, "Add files", None, QApplication.UnicodeUTF8))
        self.toolClear.setText(QApplication.translate(plugin_classname, "Clear", None, QApplication.UnicodeUTF8))
        self.label2.setText(QApplication.translate(plugin_classname, "Output directory", None, QApplication.UnicodeUTF8))
        self.label3.setText("0 files")
        self.toolDir1.setText('...')
        self.check1.setText(QApplication.translate(plugin_classname, "Replace nodata by zero", None, QApplication.UnicodeUTF8))
        self.check2.setText(QApplication.translate(plugin_classname, "Converting only (run in background)", None, QApplication.UnicodeUTF8))

        self.importButton = self.buttonBox1.button(QDialogButtonBox.Ok)
        self.importButton.setEnabled(False)
        self.importButton.setText(QApplication.translate(plugin_classname, "Import", None, QApplication.UnicodeUTF8))

        QObject.connect(self.toolFile1, SIGNAL("clicked()"), self.filedialog)
        QObject.connect(self.toolClear, SIGNAL("clicked()"), self.clear_files)
        QObject.connect(self.toolDir1, SIGNAL("clicked()"), self.directorydialog)
        QObject.connect(self.check2, SIGNAL("stateChanged(int)"), self.check2_changed)
        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("accepted()")), self.import_fgddem)
        QObject.connect(self.buttonBox1, SIGNAL(_fromUtf8("rejected()")), self.close)

        #TODO acceptDrops

        QMetaObject.connectSlotsByName(Dialog)

    def check2_changed(self, state):
        if state:
            self.importButton.setText(QApplication.translate(plugin_classname, "Convert", None, QApplication.UnicodeUTF8))
        else:
            self.importButton.setText(QApplication.translate(plugin_classname, "Import", None, QApplication.UnicodeUTF8))

    def directorydialog(self):
        file = unicode(QFileDialog.getExistingDirectory(self, "Select output directory"))
        if file != "":
            self.outDir.setText(file)

    def filedialog(self):
        names = map(str, QFileDialog.getOpenFileNames(self, "Select files to import", QDir.homePath(), _fromUtf8("JPGIS_GML files (*.zip *.xml)")))
        
        if len(names) > 0:
            existing = []
            for i in range(self.inFiles.count()):
                existing.append(unicode(self.inFiles.item(i).text()))

            for name in names:
                if not name in existing:
                    self.inFiles.addItem(name)

            self.label3.setText("%d files" % self.inFiles.count())
            self.importButton.setEnabled(True)

            if self.outDir.text() == "":
                self.outDir.setText(os.path.split(names[0])[0])

    def clear_files(self):
        self.inFiles.clear()
        self.label3.setText("0 files")
        self.importButton.setEnabled(False)

    def import_fgddem(self):
        pdir = getPluginDir()
        if pdir is None:
            QMessageBox.warning(self, self.caption, QApplication.translate(plugin_classname, 'Error: Cannot find plugin directory.', None, QApplication.UnicodeUTF8))
            return
        out_dir = unicode(self.outDir.text())
        if out_dir.find(' ') != -1:
            QMessageBox.warning(self, self.caption, QApplication.translate(plugin_classname, 'Error: Output directory cannot include any space characters.', None, QApplication.UnicodeUTF8))
            return
        options = '-out_dir "%s" ' % out_dir

        if self.check1.isChecked():
            options += '-replace_nodata_by_zero '

        names = []
        for i in range(self.inFiles.count()):
            names.append(unicode(self.inFiles.item(i).text()))

        cmd = 'python "%s/fgddem.py" %s' % (pdir, options + ' '.join(map(quote_string, names)))

        self.importButton.setEnabled(False)
        if self.check2.isChecked():
            QgsRunProcess.create(cmd, False)
        else:
            os.system(cmd)
            for i in range(len(names)):
                names[i] = os.path.join(out_dir, os.path.splitext(os.path.split(names[i])[1])[0] + '.tif')
            self.open_files(names)

    def open_files(self, names):
        for name in names:
            filetitle = os.path.splitext(os.path.split(name)[1])[0]
            layer = QgsRasterLayer(name, filetitle)
            QgsMapLayerRegistry.instance().addMapLayer(layer)

    def close(self):
        QDialog.close(self)

def quote_string(s):
    return '"' + s + '"'

