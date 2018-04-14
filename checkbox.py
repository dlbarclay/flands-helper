#!/usr/bin/env bash

from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from debugprint import dprint



class CheckBox(QStandardItem):

    def __init__(self, page, label, checked):
        QStandardItem.__init__(self, label)
        self.setCheckable(True)
        if (type(checked) == bool):
            self.setCheckState([Qt.Unchecked, Qt.Checked][checked])
        else:
            self.setCheckState(checked)
        self.setText(label)
        self.page = page

    def __repr__(self):
        return "[Page {}: {}, {}]".format(
                self.page, 
                repr(self.text()), 
                {
                    Qt.Unchecked:"Unchecked", 
                    Qt.Checked:"Checked"
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

    def getModel(self):
        # Iterate through items and build dict
        model = {}
        for i in range(self.rowCount()):
            item = self.itemFromIndex(self.index(i, 0))
            model.update({
                    item.text(): {
                        "page": item.page,
                        "label": item.text(),
                        "checked": {
                                Qt.Checked:True,
                                Qt.Unchecked:False
                            }[item.checkState()]
                    }
                })
        return model

    def dumpModel(self, indent=4):
        return json.dumps(self.model(), indent=indent)


