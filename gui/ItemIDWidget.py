from PyQt4.QtCore import QDir
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QWidget

from common import *


class ItemIDWidget(QWidget):
  read = pyqtSignal(str)  # code_label
  poke = pyqtSignal(str, int)  # code_label, new_val
  word_read = pyqtSignal(str, int)  # txt_addr, word_val
  log = pyqtSignal(str, str)  # msg, color

  def __init__(self, parent=None):
    super(ItemIDWidget, self).__init__(parent)
    self.custom_db = dict()
    self.custom_db_lines = []

    self.layout = QGridLayout(self)

    self.lbl_path_db = QLabel('DB not loaded', self)
    self.layout.addWidget(self.lbl_path_db, 0, 0, 1, 2)
    self.btn_load_db = QPushButton('Load DB', self)
    self.btn_load_db.clicked.connect(self.loadDB)
    self.layout.addWidget(self.btn_load_db, 0, 2)
    self.btn_save_db = QPushButton('Save DB', self)
    self.btn_save_db.clicked.connect(self.saveDB)
    self.layout.addWidget(self.btn_save_db, 0, 3)

    self.txt_addr = QLineEdit(self)
    self.txt_addr.setPlaceholderText('Memory Address')
    self.txt_addr.setMaxLength(10)
    self.layout.addWidget(self.txt_addr, 1, 0)
    self.btn_curval = QPushButton(' Fetch Value', self)
    self.btn_curval.setIcon(QIcon('img/flaticon/open135.png'))
    self.btn_curval.clicked.connect(self.onReadVal)
    self.layout.addWidget(self.btn_curval, 1, 1)
    self.btn_auto_incr = QPushButton('Auto Increment: OFF', self)
    self.btn_auto_incr.setCheckable(True)
    self.btn_auto_incr.setChecked(False)
    self.btn_auto_incr.clicked.connect(self.onAutoIncrChanged)
    self.layout.addWidget(self.btn_auto_incr, 1, 2)
    self.txt_type = QLineEdit(self)
    self.txt_type.setMaxLength(2)
    self.txt_type.setPlaceholderText('Type')
    self.txt_type.editingFinished.connect(self.fetchName)
    self.layout.addWidget(self.txt_type, 2, 0)
    self.txt_id = QLineEdit(self)
    self.txt_id.setMaxLength(3)
    self.txt_id.setPlaceholderText('ID')
    self.txt_id.editingFinished.connect(self.fetchName)
    self.layout.addWidget(self.txt_id, 2, 1)
    self.txt_amount = QLineEdit(self)
    self.txt_amount.setMaxLength(3)
    self.txt_amount.setPlaceholderText('Amount')
    self.layout.addWidget(self.txt_amount, 2, 2)
    self.btn_poke = QPushButton(' Poke Memory', self)
    self.btn_poke.setIcon(QIcon('img/flaticon/draw39.png'))
    self.btn_poke.clicked.connect(self.onPokeVal)
    self.layout.addWidget(self.btn_poke, 2, 3)
    self.lbl_name = QLabel('Name: [NOT IN DB]', self)
    self.layout.addWidget(self.lbl_name, 3, 0, 1, 2)
    self.txt_new_name = QLineEdit(self)
    self.txt_new_name.setPlaceholderText('Add/Modify Item Name')
    self.txt_new_name.returnPressed.connect(self.updateName)
    self.layout.addWidget(self.txt_new_name, 3, 2, 1, 2)

    self.txt_db = QPlainTextEdit(self)
    self.txt_db.setReadOnly(True)
    self.layout.addWidget(self.txt_db, 4, 0, 1, 4)

    self.layout.setColumnStretch(0, 1)
    self.layout.setColumnStretch(1, 1)
    self.layout.setColumnStretch(2, 1)
    self.layout.setColumnStretch(3, 1)

    self.setStyleSheet('ItemIDWidget { background-color: white; }')
    self.show()

  @pyqtSlot()
  def loadDB(self):
    # Get DB path
    path = QFileDialog.getOpenFileName(self, 'Load DB', QDir.currentPath() + '/codes', '*.txt')
    if len(path) <= 0:
      return
    pwd = QDir(QDir.currentPath())
    rel_path = pwd.relativeFilePath(path)
    if len(rel_path) > 2 and rel_path[:2] != '..':
      path = rel_path

    try:
      with open(str(path), 'r') as f:
        db_txt = f.read()
        try:
          self.custom_db, self.custom_db_lines = parse_item_db(db_txt)
        except BaseException, e:
          self.log.emit(str(e), 'red')
      self.txt_db.setPlainText('\n'.join(self.custom_db_lines))
      self.lbl_path_db.setText(path)
      self.log.emit('Loaded Item ID DB', 'black')
    except BaseException, e:
      self.log.emit('Failed to load Item ID DB: ' + str(e), 'red')
      traceback.print_exc()

  @pyqtSlot()
  def saveDB(self):
    path = self.lbl_path_db.text()
    if path == 'DB not loaded':
      path = QDir.currentPath() + '/codes/item_id.txt'
    path = QFileDialog.getSaveFileName(self, 'Save DB', path, '*.txt')
    if len(path) > 0:
      try:
        with open(str(path), 'w') as f:
          f.write('\n'.join(self.custom_db_lines))
        self.log.emit('Saved Item ID DB', 'black')
      except BaseException, e:
        self.log.emit('Failed to save Item ID DB: ' + str(e), 'red')
        traceback.print_exc()

  def fetchName(self):
    val_word = None
    try:
      type_txt = self.txt_type.text()
      id_txt = self.txt_id.text()
      if len(type_txt) <= 0 or len(id_txt) <= 0:
        return
      type_val = int(str(type_txt), 16)
      id_val = int(str(id_txt), 16)
      val_word = form_item_word(type_val, id_val, 0)
    except BaseException, e:
      traceback.print_exc()

    if val_word is not None:
      if val_word in self.custom_db:
        self.lbl_name.setText('Name: ' + self.custom_db[val_word].name)
        self.txt_new_name.setText(self.custom_db[val_word].name)
      else:
        self.lbl_name.setText('Name: [NOT IN DB]')

  @pyqtSlot()
  def updateName(self):
    # Parse fields
    name = self.txt_new_name.text()
    type_val = None
    id_val = None
    val_word = None
    try:
      type_val = int(str(self.txt_type.text()), 16)
      id_val = int(str(self.txt_id.text()), 16)
      val_word = form_item_word(type_val, id_val, 0)
    except ValueError, e:
      self.log.emit('Failed to fetch ID/Type/Name', 'red')
      traceback.print_exc()
    except BaseException, e:
      self.log.emit('Failed to fetch ID/Type/Name: ' + str(e), 'red')
      traceback.print_exc()

    # Update name
    if len(name) > 0 and val_word is not None:
      if val_word in self.custom_db:
        item = self.custom_db[val_word]
        item.name = name
        self.custom_db_lines[item.line] = '%02X %03X %s' % (type_val, id_val, name)
      else:
        self.custom_db[val_word] = Item(type_val, id_val, name, len(self.custom_db_lines))
        self.custom_db_lines.append('%02X %03X %s' % (type_val, id_val, name))

    # Update display
    self.txt_db.setPlainText('\n'.join(self.custom_db_lines))
    scrollbar = self.txt_db.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())

    # Automatically increment ID and poke
    if self.btn_auto_incr.isChecked():
      id_val += 1
      if id_val <= Item.MAX_ID_VAL:
        self.txt_id.setText('%03X' % id_val)
        self.txt_new_name.setText('')
        self.onPokeVal()

  def getAddrWord(self):
    addr_txt = self.txt_addr.text()
    addr_word = None
    try:
      if len(addr_txt) == 8:
        addr_word = int(str(addr_txt), 16)
      elif len(addr_txt) == 10 and addr_txt[:2] == '0x':
        addr_word = int(str(addr_txt[2:]), 16)
      else:
        addr_word = None
    except BaseException, e:
      addr_word = None
    return addr_word

  @pyqtSlot(bool)
  def onAutoIncrChanged(self, checked):
    if checked:
      self.btn_auto_incr.setText('Auto Increment: ON')
    else:
      self.btn_auto_incr.setText('Auto Increment: OFF')

  @pyqtSlot(str, int)
  def onWordRead(self, txt_addr, word_val):
    addr_word = self.getAddrWord()
    if addr_word is None:
      return

    cur_addr = '%08X' % addr_word
    if txt_addr != cur_addr:
      # print 'ItemIDWidget.onWordRead(%s != %s)' % (txt_addr, cur_addr)
      return

    (type_val, id_val, amount) = parse_item_word(word_val)
    self.txt_type.setText('%02X' % type_val)
    self.txt_id.setText('%03X' % id_val)
    self.txt_amount.setText('%d' % amount)
    self.fetchName()

  @pyqtSlot()
  def onReadVal(self):
    addr_word = self.getAddrWord()
    if addr_word is None:
      self.log.emit('Failed to parse address: invalid address, expecting XXXXXXXX', 'red')
      return

    self.read.emit('%08X' % addr_word)

  @pyqtSlot()
  def onPokeVal(self):
    addr_word = self.getAddrWord()
    if addr_word is None:
      self.log.emit('Failed to parse address: invalid address, expecting XXXXXXXX', 'red')
      return

    val_word = None
    try:
      type_val = int(str(self.txt_type.text()), 16)
      id_val = int(str(self.txt_id.text()), 16)
      amount = int(str(self.txt_amount.text()))
      if amount < 0 or amount > 0xFF:
        self.log.emit('Amount out of [0, 255] range', 'red')
        return
      val_word = form_item_word(type_val, id_val, amount)
    except BaseException, e:
      self.log.emit('Failed to fetch ID/Type/Name', 'red')
      traceback.print_exc()
      return

    if addr_word is not None and val_word is not None:
      addr = '%08X' % addr_word
      self.poke.emit(addr, val_word)
      self.read.emit(addr)
