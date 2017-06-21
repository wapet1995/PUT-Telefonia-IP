# -*- coding: utf-8 -*-
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket
from client import Client
import dialogs

class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()

        # self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('TIPspeak')
        # self.resize(500, 300)
        self.setFixedSize(500, 300)
        # self.setWindowIcon(QIcon("icons/main.png"))

        # ----------------  MENU   ---------------

        #  connection menu objects

        self.connectAction = QAction(QIcon('ikona'), '&Connect', self)
        self.connectAction.setShortcut('Ctrl+P')
        self.connectAction.setStatusTip('Connect to server')
        self.connectAction.triggered.connect(self.connectToServer)

        self.disconnectAction = QAction(QIcon('ikona'), '&Disconnect', self)
        self.disconnectAction.setShortcut('Ctrl+R')
        self.disconnectAction.setStatusTip('Disconnect from server')
        self.disconnectAction.triggered.connect(self.disconnectFromServer)
        self.disconnectAction.setEnabled(False)

        self.exitFromChannelAction = QAction(QIcon('ikona'), '&Exit channel', self)
        self.exitFromChannelAction.setShortcut('Ctrl+R')
        self.exitFromChannelAction.setStatusTip('Exit from channel')
        self.exitFromChannelAction.triggered.connect(self.exitFromChannel)
        self.exitFromChannelAction.setEnabled(False)

        exitAction = QAction(QIcon('ikona'), '&Close', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Close application')
        exitAction.triggered.connect(self.quit)

        # administration menu objects

        addChannelAction = QAction(QIcon('ikona'), '&Add channel', self)
        addChannelAction.setStatusTip('Add channel')
        addChannelAction.triggered.connect(self.addChannel)

        delChannelAction = QAction(QIcon('ikona'), '&Delete channel', self)
        delChannelAction.setStatusTip('Delete channel')
        delChannelAction.triggered.connect(self.delChannel)

        blockNickAction = QAction(QIcon('ikona'), '&Block nickname', self)
        blockNickAction.setStatusTip('Block nickname')
        blockNickAction.triggered.connect(self.blockNick)

        unblockNickAction = QAction(QIcon('ikona'), '&Unblock nickname', self)
        unblockNickAction.setStatusTip('Unblock nickname')
        unblockNickAction.triggered.connect(self.unblockNick)

        blockIPAction = QAction(QIcon('ikona'), '&Block IP', self)
        blockIPAction.setStatusTip('Block IP')
        blockIPAction.triggered.connect(self.blockIPAddress)

        unblockIPAction = QAction(QIcon('ikona'), '&Unblock IP', self)
        unblockIPAction.setStatusTip('Unblock IP')
        unblockIPAction.triggered.connect(self.unblockIPAddress)

        # help

        authorsAction = QAction(QIcon('ikona'), '&Authors', self)
        authorsAction.setStatusTip('Show authors')
        authorsAction.triggered.connect(self.credits)

        menubar = self.menuBar()

        # connection tab
        connectionMenu = menubar.addMenu('&Connection')
        connectionMenu.addAction(self.connectAction)
        connectionMenu.addAction(self.disconnectAction)
        connectionMenu.addAction(self.exitFromChannelAction)
        connectionMenu.addAction(exitAction)

        # administration tab
        self.adminMenu = menubar.addMenu('&Administration')
        self.adminMenu.addAction(addChannelAction)
        self.adminMenu.addAction(delChannelAction)
        self.adminMenu.addAction(blockNickAction)
        self.adminMenu.addAction(unblockNickAction)
        self.adminMenu.addAction(blockIPAction)
        self.adminMenu.addAction(unblockIPAction)
        self.adminMenu.setEnabled(False)

        # help tab
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(authorsAction)

        # -------------   MIDDLE    ---------------------
        middle = QWidget()  # srodkowy widget
        grid = QGridLayout()  # layout srodkowego widgetu

        # Server status
        self.conn_status = QLabel("Not connected to server")
        self.conn_status.setStyleSheet("color : red;")
        self.conn_status.setMaximumHeight(30)
        grid.addWidget(self.conn_status, 0, 1)

        # My IP address
        self.my_ip_addr = QLabel("My IP: ")
        self.my_ip_addr.setMaximumHeight(30)
        grid.addWidget(self.my_ip_addr, 0, 0)
        
        # Channels - layout and settings
        self.chosen_channel = QLabel("Channels")
        self.chosen_channel.setMaximumHeight(30)
        grid.addWidget(self.chosen_channel, 1, 0)
        self.channelsGroupFrame = QFrame()
        self.channelsGroupFrame.setStyleSheet(
            "background-color: #D6D6D6; border: 1px solid black; border-radius: 10px;")

        channelsGroupLayout = QVBoxLayout()
        self.channelsTree = QTreeWidget()
        self.channelsTree.setStyleSheet("background: #D6D6D6; font-size: 18px; border: none;")
        self.channelsTree.setHeaderHidden(True)
        self.channelsTree.itemDoubleClicked.connect(self.enterChannel)

        channelsGroupLayout.addWidget(self.channelsTree)
        self.channelsGroupFrame.setLayout(channelsGroupLayout)
        grid.addWidget(self.channelsGroupFrame, 2, 0)

        # Users - layout and settings
        self.chosen_nick = QLabel("Users")
        self.chosen_nick.setMaximumHeight(30)
        grid.addWidget(self.chosen_nick, 1, 1)
        self.usersGroupFrame = QFrame()
        self.usersGroupFrame.setStyleSheet("background-color: #D6D6D6; border: 1px solid black; border-radius: 10px;")

        usersGroupLayout = QVBoxLayout()
        self.usersTree = QTreeWidget()
        self.usersTree.setStyleSheet("background: #D6D6D6; font-size: 18px; border: none; color: green;")
        self.usersTree.setHeaderHidden(True)
        self.usersTree.setContextMenuPolicy(Qt.CustomContextMenu)

        usersGroupLayout.addWidget(self.usersTree)
        self.usersGroupFrame.setLayout(usersGroupLayout)
        grid.addWidget(self.usersGroupFrame, 2, 1)

        middle.setLayout(grid)
        self.setCentralWidget(middle)

        # -------------   STATUSBAR  --------------------
        self.statusBar().showMessage('Not connected')

        self.globalVariables()
        self.show()

    def globalVariables(self):
        self.CONNECTION = None  # Client object
        # TIMERS
        self.timer_channels = QTimer()
        self.timer_channels.timeout.connect(self.refreshChannelsTree)
        self.timer_channels.setInterval(2000)

        self.timer_users = QTimer()
        self.timer_users.timeout.connect(self.refreshUsersTree)
        self.timer_users.setInterval(2000)



    # --------------------------    Auxiliary functions      -------------------------------
    def validateIPv4(self, addr):
        addr = addr.split(".")
        if len(addr) == 4:
            try:
                if 0 <= int(addr[0]) < 255 and 0 <= int(addr[1]) < 255 and \
                    0 <= int(addr[2]) < 255 and 0 <= int(addr[3]) < 255:
                    return True
            except:
                return False
        return False

    # --------------------------    Connection - EVENTS      -------------------------------

    def connectToServer(self):
        # run from Menu->Polacz
        # connect to server with given IP address, port and unique nick
        conn = dialogs.ConnectDialog(self)
        if conn.exec_():
            #print("Łącze z serwerem")
            server_ip = str(conn.ip_address.text())
            server_port = conn.port_number.value()
            nick = str(conn.nick.text())
            admin_password = str(conn.admin_password.text())
            self.CONNECTION = Client(nick, server_ip, server_port)
            if self.CONNECTION.connect(admin_password): # return True
                print("Połączono")
                self.statusBar().showMessage('Connected')
                self.conn_status.setText("Server IP: " + server_ip)
                self.conn_status.setStyleSheet("color: green;")
                self.my_ip_addr.setText("My IP: " + self.CONNECTION.MY_IP_ADDRESS)
                self.connectAction.setEnabled(False)
                self.disconnectAction.setEnabled(True)
                if self.CONNECTION.IAM_ADMIN:
                    self.adminMenu.setEnabled(True)
                self.timer_channels.start()
                self.refreshChannelsTree()
                self.chosen_nick.setText("Nick: " + nick)
            else:
                self.CONNECTION = None
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(u":(")
                msg.setText(u"""Nie można podłączyć się do serwera\n
                    Możliwe przyczyny:
                    - adres IP jest zablokowany
                    - nick jest zajęty lub zablokowany
                    - niepoprawny adres IP serwera
                    """)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                #print("Nie połączono - nick jest zajęty lub zablokowany")
                self.statusBar().showMessage('Not connected')


    def refreshChannelsTree(self):
        if not self.CONNECTION.getChannelsList():
            self.kickedFromServer()
            return
        self.channelsTree.clear()

        if self.CONNECTION is None:
            print("Błąd połączenia podczas odświeżania listy kanałów")

        for i in self.CONNECTION.CHANNELS_LIST:
            tmp = QTreeWidgetItem()
            tmp.setText(0, str(i))
            self.channelsTree.addTopLevelItem(tmp)
        if self.CONNECTION.CURRENT_CHANNEL is not None and \
            self.CONNECTION.CURRENT_CHANNEL not in self.CONNECTION.CHANNELS_LIST:
            self.exitFromChannel()


    def enterChannel(self, item, column):
        self.timer_channels.stop()  # stop update channels for moment
        if self.timer_users.isActive():
            self.timer_users.stop()
        if self.CONNECTION.CURRENT_CHANNEL is not None:
            if self.CONNECTION.exitChannel():
                password, result = QInputDialog.getText(self, 'Password for channel', 'Enter password:')
                if result and self.CONNECTION.joinChannel(item.text(column), password):
                    #print("Wszedłeś do kanału")
                    self.chosen_channel.setText("Channel: " + self.CONNECTION.CURRENT_CHANNEL)
                else:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle(u":(")
                    msg.setText(u"Błędne hasło")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
            else:
                #print("Błąd podczas wychodzenia z kanału. (1)")
                self.timer_channels.start()
                return
        else:
            password, result = QInputDialog.getText(self, 'Password for channel', 'Enter password:')
            if result and self.CONNECTION.joinChannel(item.text(column), password):
                #print("Wszedłeś do kanału")
                self.chosen_channel.setText("Channel: " + self.CONNECTION.CURRENT_CHANNEL)
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle(u":(")
                msg.setText(u"Błędne hasło")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                self.timer_channels.start()
                return
        
        self.exitFromChannelAction.setEnabled(True)
        self.timer_channels.start()
        self.timer_users.start()
        self.refreshUsersTree()


    def refreshUsersTree(self):
        if not self.CONNECTION.getChannelUsers(self.CONNECTION.CURRENT_CHANNEL):
            self.kickedFromServer()
            return
        self.usersTree.clear()

        if self.CONNECTION is None:
            pass
            #print("Błąd połączenia podczas odświeżania listy użytkowników")

        for i in self.CONNECTION.CURRENT_CHANNEL_USERS:
            tmp = QTreeWidgetItem()
            tmp.setText(0, str(i))
            self.usersTree.addTopLevelItem(tmp)

    def exitFromChannel(self):
        #print("Wyjście z kanału")
        self.CONNECTION.exitChannel()
        self.timer_users.stop()
        self.usersTree.clear()
        self.exitFromChannelAction.setEnabled(False)
        self.chosen_channel.setText("Channels")


    def disconnectFromServer(self):
        #print("Rozłączam od serwera")
        self.exitFromChannelAction.setEnabled(False)
        if self.CONNECTION.disconnect():
            #print("Rozłączono")
            self.connectAction.setEnabled(True)  # disable connection button in menu
            self.disconnectAction.setEnabled(False)
            self.CONNECTION = None
            self.channelsTree.clear()
            self.usersTree.clear()
            self.conn_status.setText("Not connected to server")
            self.conn_status.setStyleSheet("color: red;")
            self.statusBar().showMessage('Disconnected')
            self.timer_users.stop()
            self.timer_channels.stop()
            self.chosen_nick.setText("Users")
            self.chosen_channel.setText("Channels")
            return True
        else:
            #print("Błąd rozłączania. Spróbuj jeszcze raz.")
            return False

    def kickedFromServer(self):
        #print("Rozłączam od serwera")
        self.CONNECTION.AUDIO_LOCK = False
        self.exitFromChannelAction.setEnabled(False)
        self.connectAction.setEnabled(True)  # disable connection button in menu
        self.disconnectAction.setEnabled(False)
        self.CONNECTION = None
        self.channelsTree.clear()
        self.usersTree.clear()
        self.conn_status.setText("Not connected to server")
        self.conn_status.setStyleSheet("color: red;")
        self.statusBar().showMessage('Disconnected')
        self.timer_users.stop()
        self.timer_channels.stop()
        self.chosen_nick.setText("Users")
        self.chosen_channel.setText("Channels")
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(u":(")
        msg.setText(u"Wyrzucono Cię z serwera")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        sys.exit(0)



    def quit(self):
        if self.CONNECTION is None:
            sys.exit(0)
        elif self.disconnectFromServer():
            sys.exit(0)
        else:
            print("Spróbuj wyjść jeszcze raz")


    # ---------------------------     Administration - EVENTS     -------------------------------

    def addChannel(self):
        tmp = dialogs.AddChannelDialog(self)
        if tmp.exec_():
            self.CONNECTION.addChannel(tmp.name.text(), tmp.password.text())
            #print("Dodanie kanału ", tmp.name.text(), " z hasłem ", tmp.password.text())
            self.refreshChannelsTree()

    def delChannel(self):
        channel, result = QInputDialog.getItem(self, "Delete channel", "Name", self.CONNECTION.CHANNELS_LIST, 0, False)
        if result:
            self.CONNECTION.delChannel(channel)
            #print("Usunięto ", channel)
            self.refreshChannelsTree()

    def blockNick(self):
        tmp = dialogs.BlockNickDialog(self)
        if tmp.exec_():
            if self.CONNECTION.blockNick(tmp.nickname.text(), tmp.cause.text()):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(u":)")
                msg.setText(u"Zablokowano " + tmp.nickname.text())
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(u":(")
                msg.setText(u"Nie udało się zablokować " + tmp.nickname.text())
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def unblockNick(self):
        nick, result = QInputDialog.getText(self, 'Unblock nickname', 'Type nickname:')
        if result:
            if self.CONNECTION.unblockNick(nick):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(u":)")
                msg.setText(u"Odblokowano " + nick)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(u":(")
                msg.setText(u"Nie udało się odblokować " + nick)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def blockIPAddress(self):
        tmp = dialogs.BlockIPDialog(self)
        if tmp.exec_():
            if self.CONNECTION.blockIP(tmp.ip.text(), tmp.cause.text()):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(u":)")
                msg.setText(u"Zablokowano " + tmp.ip.text())
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(u":(")
                msg.setText(u"Nie udało się zablokować " + tmp.ip.text())
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def unblockIPAddress(self):
        tmp = dialogs.UnBlockIPDialog(self)
        if tmp.exec_():
            if self.CONNECTION.unblockIP(tmp.ip.text()):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(u":)")
                msg.setText(u"Odblokowano " + tmp.ip.text())
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(u":(")
                msg.setText(u"Nie udało się odblokować " + tmp.ip.text())
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    # ----------------------    HELP - EVENTS     -------------------------------

    def credits(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Authors")
        msg.setText("Krzysztof Łuczak <br/> Maciej Marciniak")
        msg.setInformativeText("")
        msg.setDetailedText("https://github.com/wapet1995/PUT-Telefonia-IP")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
