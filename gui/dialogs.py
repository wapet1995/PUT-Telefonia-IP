# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import netifaces

class ConnectDialog(QDialog):
    def __init__(self, parent = None):
        super(ConnectDialog, self).__init__(parent)
        #self.resize(650, 400)
        #self.move(300, 250)
        self.setWindowTitle("Connect to server")
        layout = QGridLayout(self)
        #self.layout.setSpacing(10)

        # My IP address
        _lab0 = QLabel("My IP address: ")
        self.my_ip_address = QComboBox()
        self.my_ip_address.addItems(self.list_interfaces())

        # Server IP address
        _lab1 = QLabel("Server IP address: ")
        self.server_ip_address = QLineEdit()
        self.server_ip_address.setMaxLength(15)

        # port
        _lab2 = QLabel("Port: ")
        port_number = QSpinBox()
        port_number.setRange(1025,65535)
        port_number.setValue(50900)

        # nick
        _lab3 = QLabel("Nickname: ")
        nick = QLineEdit()

        layout.addWidget(_lab0,0,0)
        layout.addWidget(self.my_ip_address,0,1)
        layout.addWidget(_lab1,1,0)
        layout.addWidget(self.server_ip_address,1,1)
        layout.addWidget(_lab2,2,0)
        layout.addWidget(port_number,2,1)
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
        if self.validate_ipv4(self.server_ip_address.text()):
            self.accept()

    def clickCancel(self):
        self.reject()

    def validate_ipv4(self, addr):
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

    def list_interfaces(self):
        ip_list = QStringList()
        for iface in netifaces.interfaces():
            try:
                ip_addr = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                ip_list.append(ip_addr)
            except:
                pass
        return ip_list


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