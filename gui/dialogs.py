# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ConnectDialog(QDialog):
    def __init__(self, parent = None):
        super(ConnectDialog, self).__init__(parent)
        #self.resize(650, 400)
        #self.move(300, 250)
        self.setWindowTitle("Connect to server")
        layout = QGridLayout(self)
        #self.layout.setSpacing(10)

        
        # IP address
        _lab1 = QLabel("IP address: ")
        self.ip_address = QLineEdit()

        # port
        _lab2 = QLabel("Port: ")
        port_number = QSpinBox()
        port_number.setRange(1025,65535)
        port_number.setValue(50900)

        # nick
        _lab3 = QLabel("Nickname: ")
        nick = QLineEdit()

        layout.addWidget(_lab1,0,0)
        layout.addWidget(self.ip_address,0,1)
        layout.addWidget(_lab2,1,0)
        layout.addWidget(port_number,1,1)
        layout.addWidget(_lab3,3,0)
        layout.addWidget(nick,3,1)

        # OK
        con = QPushButton("Connect")
        layout.addWidget(con, 4,1)
        con.clicked.connect(self.clickOk)
        # Anuluj
        cancel = QPushButton("Cancel")
        layout.addWidget(cancel, 4,0)
        cancel.clicked.connect(self.clickCancel)

    def clickOk(self):
        if self.validateIPv4(self.ip_address.text()):
            self.accept()

    def clickCancel(self):
        self.reject()

    def validateIPv4(self, addr):
        addr = addr.split(".")
        if len(addr) == 4:
            try:
                if int(addr[0]) >= 0 and int(addr[0]) < 255 and \
                    int(addr[1]) >= 0 and int(addr[1]) < 255 and \
                    int(addr[2]) >= 0 and int(addr[2]) < 255 and \
                    int(addr[3]) >= 0 and int(addr[3]) < 255:
                    return True
            except:
                return False
        return False


class AddChannelDialog(QDialog):
    def __init__(self, parent = None):
        super(AddChannelDialog, self).__init__(parent)
        #self.resize(650, 400)
        #self.move(300, 250)
        self.setWindowTitle("Add channel")
        layout = QGridLayout(self)
        
        # IP address
        _lab1 = QLabel("Name: ")
        self.name = QLineEdit()

        # port
        _lab2 = QLabel("Password: ")
        self.password = QLineEdit()


        layout.addWidget(_lab1,0,0)
        layout.addWidget(self.name,0,1)
        layout.addWidget(_lab2,1,0)
        layout.addWidget(self.password,1,1)

        # OK
        add = QPushButton("Add")
        layout.addWidget(add, 3,1)
        add.clicked.connect(self.clickOk)
        # Anuluj
        cancel = QPushButton("Cancel")
        layout.addWidget(cancel, 3,0)
        cancel.clicked.connect(self.clickCancel)

    def clickOk(self):
        if ' ' in self.name.text() or ' ' in self.password.text() or self.name.text() == '':
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(u"Little error")
            msg.setText(u"Channel name should consist of one word.\nPassword can be empty.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
        self.accept()

    def clickCancel(self):
        self.reject()