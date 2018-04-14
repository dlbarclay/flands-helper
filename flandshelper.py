#!/usr/bin/env python3

import os
import sys
import json
from shutil import copyfile

#from PyQt5.QtCore import Qt
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QObject, QFileSelector
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QComboBox, QLabel, \
    QLineEdit, QListWidget, QListView, QMenuBar, QMenuBar, QToolBar, \
    QApplication, QWidget, QMainWindow, QStatusBar

from debugprint import dprint, setDebugPrint
from checkbox import CheckBox, CheckBoxListModel


DEFAULT_MODEL = {
    "book1": {},
    "book2": {},
    "book3": {},
    "book4": {},
    "book5": {},
    "book6": {},
    "book7": {},
#    "book8": {},
#    "book9": {},
#    "book10": {},
#    "book11": {},
#    "book12": {},
}


def createModelJson():
    f = open("model.json", "w")
    json.dump(DEFAULT_MODEL, f)
    f.close()



class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        
        self.loadModelFromFile()

        self.initUI()
        
        self.loadCurrentBook()

    def loadBook(self, book):
        self.listModel.loadModel(self.model[book])

    def loadCurrentBook(self):
        book = "book{}".format(self.bookSelector.currentIndex() + 1)
        self.loadBook(book)

    def saveCurrentBook(self):
        book = "book{}".format(self.bookSelector.currentIndex() + 1)
        self.model.update({book: self.listModel.getModel()})

    def loadModelFromFile(self, filename="model.json"):
        try:
            os.stat(filename)
            copyfile(filename, filename + ".backup")
        except (OSError,IOError):
            createModelJson()
        f = open(filename, 'r')
        self.setModel(json.load(f))
        f.close()

    def saveModelToFile(self, filename="model.json"):
        mw.saveCurrentBook()
        f = open(filename, "w")
        json.dump(mw.model, f, indent=4, sort_keys=True)
        f.close()

    def setModel(self, model):
        self.model = model

    def resetModel(self):
        self.setModel(DEFAULT_MODEL)

    def resetAllCheckboxes(self):
        self.resetModel()
        self.loadCurrentBook()

    def insertCheckBox(self, number, checked=QtCore.Qt.Checked, label=None):
        if (label == None):
            label = str(number)
        item = CheckBox(number, label, checked)
        self.listModel.insertCheckBox(item)
        index = self.listModel.indexFromItem(item)
        return index

    def addCheckboxFromInput(self):
        book = self.bookSelector.currentIndex() + 1
        text = self.pageInput.text()
        checked = self.addCheckBox.checkState()

        try:
            page = int(text)
        except ValueError:
            return None

        # Insert a checkbox entry
        self.insertCheckBox(page, checked=checked)
        self.saveCurrentBook()

    def on_addButtonReleased(self):
        self.addCheckboxFromInput()

    def on_pageInputReturnPressed(self):
        self.addCheckboxFromInput()

    def on_delButtonReleased(self):
        index = self.listView.currentIndex()

        # No row selected
        if (index.row() < 0):
            return 0

        self.listModel.removeRow(index.row())
        self.saveCurrentBook()

    def on_bookSelectorChanged(self):
        self.loadCurrentBook()

    def on_itemChanged(self):
        self.saveCurrentBook()

    def on_actionLoad(self):
        f = Qt.QFileDialog.getOpenFileName(self, filter='JSON Files (*.json)')
        fname = f[0]
        if (fname != ''):
            #dprint("Load: ", fname[0])
            try:
                #TODO Verify valid model
                self.loadModelFromFile(fname) 
                self.loadCurrentBook()
            except (ValueError,KeyError):
                dprint("MainWindow.on_actionLoad: Error loading model from file.")

    def on_actionSaveAs(self):
        f = Qt.QFileDialog.getSaveFileName(self, filter='JSON Files (*.json)')
        fname = f[0]
        if (not fname.endswith(".json")):
            fname += ".json"
        if (fname != ''):
            #TODO Verify valid filename and path
            dprint("SaveAs: ", fname)
            #TODO Handle OS errors in saving file
            self.saveModelToFile(fname)

    def on_actionReset(self):
        yesno = Qt.QMessageBox.question(self, "WARNING: Reset All", "Are you sure you want to clear ALL checkbox entries, including deleting all checkboxes?", 
            Qt.QMessageBox.Yes | Qt.QMessageBox.Cancel, Qt.QMessageBox.Cancel)
        if (yesno == Qt.QMessageBox.Yes):
            self.resetAllCheckboxes()

    def initUI(self):
        self.setWindowIcon(QIcon("tickbox64.png"))
        uic.loadUi("mainwindow.ui", self)

        self.listModel = CheckBoxListModel(self.listView)
        self.listView.setModel(self.listModel)

        #TODO De-select listView when clicking outside of view
        #TODO De-select listView when pressing ESC

        #TODO Delete entry by pressing DELETE
        self.addButton.released.connect(self.on_addButtonReleased)
        self.pageInput.returnPressed.connect(self.on_pageInputReturnPressed)
        #TODO Add entry by pressing ENTER
        self.delButton.released.connect(self.on_delButtonReleased)
        self.bookSelector.currentIndexChanged.connect(self.on_bookSelectorChanged)
        self.listModel.itemChanged.connect(self.on_itemChanged)

        self.actionLoad.triggered.connect(self.on_actionLoad)
        self.actionSaveAs.triggered.connect(self.on_actionSaveAs)
        self.actionReset.triggered.connect(self.on_actionReset)

        #help(QtCore.QModelIndex)
        #help(self.listView)
        #help(self.listModel)
        #help(self.bookSelector)
        #help(self.pageInput)

        #self.show()

    def closeEvent(self, event):
        self.saveModelToFile()
        event.accept()


if (__name__ == "__main__"):

    if ("DEBUG" in os.environ.keys()):
        setDebugPrint(True)

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rc = app.exec_()
    sys.exit(rc)
