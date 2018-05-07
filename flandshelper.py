#!/usr/bin/env python3

#TODO Add support for loading book QComboBox items from model
#TODO Add support for adding new books
#TODO Add support for deleting specific books

import os
import sys
import json
import traceback
from shutil import copyfile

#from PyQt5.QtCore import Qt
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QObject, QFileSelector
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, \
    QLineEdit, QListView, QMenuBar, QMenuBar, QToolBar, QStatusBar, QLabel, \
    QVBoxLayout, QHBoxLayout, QComboBox

from debugprint import dprint, setDebugPrint
from checkbox import CheckBox, CheckBoxListModel


if (getattr(sys, "_MEIPASS", None) is None):
    dprint("No resource path specified. Using current directory")


def resource_path(relative):
    basepath = getattr(sys, "_MEIPASS", os.getcwd())
    path = os.path.join(basepath, relative)
    dprint(path)
    return path


DEFAULT_MODEL = {
    "Book 1": {},
    "Book 2": {},
    "Book 3": {},
    "Book 4": {},
    "Book 5": {},
    "Book 6": {},
    "Book 7": {},
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

    def loadBooks(self):
        self.bookSelector.clear()

        books = sorted(self.model.keys())
        for book in books:
            self.bookSelector.addItem(book)

    def loadBook(self, book):
        self.listModel.loadModel(self.model[book])

    def loadCurrentBook(self):
        #book = "book{}".format(self.bookSelector.currentIndex() + 1)
        book = self.bookSelector.currentText()
        self.loadBook(book)

    def saveCurrentBook(self):
        #book = "book{}".format(self.bookSelector.currentIndex() + 1)
        book = self.bookSelector.currentText()
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

    def closeEvent(self, event):
        self.saveModelToFile()
        event.accept()

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

    def toggleSelectedCheckbox(self):
        checkbox = self.listModel.itemFromIndex(self.listView.currentIndex())
        if (checkbox != None):
            checkbox.toggle()

    def delSelectedCheckbox(self):
        index = self.listView.currentIndex()

        # No row selected
        if (index.row() < 0):
            return 0

        self.listModel.removeRow(index.row())
        self.saveCurrentBook()

    def deselectCheckbox(self):
        self.listView.clearSelection()
        self.listView.setCurrentIndex(self.listModel.index(-1,0))

    def on_addButtonReleased(self):
        self.addCheckboxFromInput()

    def on_pageInputReturnPressed(self):
        self.addCheckboxFromInput()

    def on_listViewKeyPressed(self, ev):
        #print("QListView - Key Pressed:", ev.key())
        if (ev.key() == QtCore.Qt.Key_Delete):
            self.delSelectedCheckbox()
        elif (ev.key() == QtCore.Qt.Key_Space):
            self.toggleSelectedCheckbox()
        elif (ev.key() == QtCore.Qt.Key_Escape):
            self.deselectCheckbox()

    def on_delButtonReleased(self):
        self.delSelectedCheckbox()

    def on_bookSelectorChanged(self):
        self.loadCurrentBook()

    def on_itemChanged(self):
        self.saveCurrentBook()

    def on_actionLoad(self):
        f = Qt.QFileDialog.getOpenFileName(self, filter='JSON Files (*.json)')
        fname = f[0]
        if (fname != ''):
            dprint("Load: ", fname[0])
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
            try:
                #TODO Handle OS errors in saving file
                self.saveModelToFile(fname)
            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tbf = traceback.format_exception(exc_type, exc_value, exc_tb)
                tbs = "".join(tbf)
                print(tbs, end='')
                errormessage = "Error: " + repr(e) + "\n\n" + tbs
                QMessageBox.about(self, "Error", errormessage)

    def on_actionReset(self):
        yesno = Qt.QMessageBox.question(self, "WARNING: Reset All", "Are you sure you want to clear ALL checkbox entries, including deleting all checkboxes?", 
            Qt.QMessageBox.Yes | Qt.QMessageBox.Cancel, Qt.QMessageBox.Cancel)
        if (yesno == Qt.QMessageBox.Yes):
            self.resetAllCheckboxes()

    def initUI(self):
        self.setWindowIcon(QIcon(resource_path(
                os.path.join("res","tickbox.ico"))))
        uic.loadUi(resource_path(
                os.path.join("res","mainwindow.ui")), self)

        self.loadBooks()

        self.listModel = CheckBoxListModel(self.listView)
        self.listView.setModel(self.listModel)

        #TODO De-select listView when clicking outside of view
        #   Intercept all mouse events?
        #   Assign default mouse event handler to all classes?

        self.addButton.released.connect(self.on_addButtonReleased)
        self.pageInput.returnPressed.connect(self.on_pageInputReturnPressed)
        self.delButton.released.connect(self.on_delButtonReleased)
        self.listView.keyPressEvent = self.on_listViewKeyPressed
        self.bookSelector.currentIndexChanged.connect(self.on_bookSelectorChanged)
        self.listModel.itemChanged.connect(self.on_itemChanged)

        self.actionLoad.triggered.connect(self.on_actionLoad)
        self.actionSaveAs.triggered.connect(self.on_actionSaveAs)
        self.actionReset.triggered.connect(self.on_actionReset)


if (__name__ == "__main__"):

    if ("DEBUG" in os.environ.keys()):
        setDebugPrint(True)

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rc = app.exec_()
    sys.exit(rc)
