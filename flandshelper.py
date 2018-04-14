#!/usr/bin/env python3

import os
import sys
import json
from shutil import copyfile

#from PyQt5.QtCore import Qt
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QObject, QFileSelector
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QComboBox, QLabel, \
    QLineEdit, QListWidget, QListView, QMenuBar, QMenuBar, QToolBar, \
    QApplication, QWidget, QMainWindow, QStatusBar

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

DEBUG=False
#DEBUG=True

def dprint(*args, **nargs):
    global DEBUG
    if (DEBUG):
        print(*args, **nargs)

def createModelJson():
    f = open("model.json", "w")
    json.dump(DEFAULT_MODEL, f)
    f.close()

class CheckBox(QStandardItem):

    def __init__(self, page, label, checked):
        QStandardItem.__init__(self, label)
        self.setCheckable(True)
        if (type(checked) == bool):
            self.setCheckState([QtCore.Qt.Unchecked, QtCore.Qt.Checked][checked])
        else:
            self.setCheckState(checked)
        self.setText(label)
        self.page = page

    def __repr__(self):
        return "[Page {}: {}, {}]".format(
                self.page, 
                repr(self.text()), 
                {
                    QtCore.Qt.Unchecked:"Unchecked", 
                    QtCore.Qt.Checked:"Checked"
                 }[self.checkState()]
            )

    def equals(self, other):
        return ((self.page == other.page) and (self.text() == other.text()))
        #    and (self.checkState() == other.checkState())

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    def __gt__(self, other):
        if (self.page == other.page):
            return self.text() > other.text()
        else:
            return self.page > other.page

    def __ge__(self, other):
        if (self.page == other.page):
            return self.text() >= other.text()
        else:
            return self.page > other.page

    def __lt__(self, other):
        if (self.page == other.page):
            return self.text() < other.text()
        else:
            return self.page < other.page

    def __le__(self, other):
        if (self.page == other.page):
            return self.text() <= other.text()
        else:
            return self.page < other.page


class CheckBoxListModel(QStandardItemModel):

    def __init__(self, parent=None, model=None):
        QStandardItemModel.__init__(self)

        if (model != None):
            self.loadModel(model)

    # Find the index into which to insert the checkbox. 
    # Insertion into listView counting backwards through indices.
    # @param    checkbox - the CheckBox item to find the index of insertion
    # @return   index - int index of item insertion
    def _insertIndex(self, checkbox):
        # Insertion sort for now
        index = self.rowCount()
        for i in reversed(range(self.rowCount())):
            item = self.itemFromIndex(self.index(i, 0))
            if (checkbox < item):
                index = i
            elif (checkbox.equals(item)):
                index = i# + 1
            else:
                dprint(checkbox, " > ", item)
                break
        
        return index

    # Insert checkbox into listView at given integer index
    # @param    index - index which to insert the item into listView
    # @param    checkbox - the CheckBox item to insert into listView
    def insertCheckBoxAt(self, index, checkbox):
        self.insertRow(index, checkbox)

    # Insert checkbox into listView at sorted position
    # @param checkbox - the CheckBox item to insert into listView
    def insertCheckBox(self, checkbox):
        index = self._insertIndex(checkbox)
        existing = self.itemFromIndex(self.index(index, 0))
        dprint("Attempting insert at index:", index)
        if ((existing is None) or (not checkbox.equals(existing))):
            dprint("Existing:", existing)
            self.insertCheckBoxAt(index, checkbox)
        else:
            dprint("Ex:", existing, "  New:",checkbox, "  Eq:",checkbox.equals(existing))
            dprint("Identical checkbox found. Rejecting insert")

    def loadModel(self, model, clearExisting=True):
        if clearExisting:
            self.clear()
        # Sort checkboxes by page number/label
        for box in model.values():
            self.insertCheckBox(CheckBox(
                    box["page"], box["label"], box["checked"]
                ))

    def model(self):
        # Iterate through items and build dict
        model = {}
        for i in range(self.rowCount()):
            item = self.itemFromIndex(self.index(i, 0))
            model.update({
                    item.text(): {
                        "page": item.page,
                        "label": item.text(),
                        "checked": {
                                QtCore.Qt.Checked:True, 
                                QtCore.Qt.Unchecked:False
                            }[item.checkState()]
                    }
                })
        return model
        
    def dumpModel(self, indent=4):
        return json.dumps(self.model(), indent=indent)
        


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
        self.model.update({book: self.listModel.model()})

    def loadModelFromFile(self, filename="model.json"):
        try:
            os.stat(filename)
            copyfile(filename, filename + ".backup")
        except (OSError,IOError):
            createModelJson()
        f = open(filename, 'r')
        self.model = json.load(f)
        f.close()

    def saveModelToFile(self, filename="model.json"):
        mw.saveCurrentBook()
        f = open(filename, "w")
        json.dump(mw.model, f, indent=4, sort_keys=True)
        f.close()

    def resetModel(self):
        self.model = DEFAULT_MODEL

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
        fname = Qt.QFileDialog.getOpenFileName(self, filter='JSON Files (*.json)')
        #dprint("Load: ", fname[0])
        try:
            #TODO Verify valid model
            self.loadModelFromFile(fname[0]) 
        except (ValueError,KeyError):
            dprint("MainWindow.on_actionLoad: Error loading model from file.")

    def on_actionSaveAs(self):
        fname = Qt.QFileDialog.getSaveFileName(self, filter='JSON Files (*.json)')
        #TODO Verify valid filename and path
        dprint("SaveAs: ", fname[0])
        #TODO Handle OS errors in saving file
        self.saveModelToFile(fname[0])

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
        DEBUG=True

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    rc = app.exec_()
    sys.exit(rc)
