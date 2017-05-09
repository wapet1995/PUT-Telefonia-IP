# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import dialogs

class GUI(QMainWindow):
    
    def __init__(self):
        super(GUI, self).__init__()

        #self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('TIPspeak')
        #self.resize(500, 300)
        self.setFixedSize(500, 300)
        #self.setWindowIcon(QIcon("icons/main.png"))

        # ----------------  MENU   ---------------

        #  connection menu objects

        connectAction = QAction(QIcon('ikona'), '&Connect', self)
        connectAction.setShortcut('Ctrl+P')
        connectAction.setStatusTip('Connect to server')
        connectAction.triggered.connect(self.connectToServer)

        disconnectAction = QAction(QIcon('ikona'), '&Disconnect', self)
        disconnectAction.setShortcut('Ctrl+R')
        disconnectAction.setStatusTip('Disconnect from server')
        disconnectAction.triggered.connect(self.disconnectFromServer)

        exitChannel = QAction(QIcon('ikona'), '&Exit channel', self)
        exitChannel.setShortcut('Ctrl+E')
        exitChannel.setStatusTip('Exit from server')
        exitChannel.triggered.connect(self.exitFromChannel)

        exitAction = QAction(QIcon('ikona'), '&Close', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Close application')
        exitAction.triggered.connect(self.quit)

        # administration menu objects

        addChannelAction = QAction(QIcon('ikona'), '&Add channel', self)
        #addChannelAction.setShortcut('Ctrl+A')
        addChannelAction.setStatusTip('Add channel')
        addChannelAction.triggered.connect(self.addChannel)

        delChannelAction = QAction(QIcon('ikona'), '&Delete channel', self)
        #delChannelAction.setShortcut('Ctrl+A')
        delChannelAction.setStatusTip('Delete channel')
        delChannelAction.triggered.connect(self.delChannel)

        blockNickAction = QAction(QIcon('ikona'), '&Block nickname', self)
        #blockNickAction.setShortcut('Ctrl+A')
        blockNickAction.setStatusTip('Block nickname')
        blockNickAction.triggered.connect(self.blockNick)

        blockIPAction = QAction(QIcon('ikona'), '&Block IP', self)
        #blockIPAction.setShortcut('Ctrl+A')
        blockIPAction.setStatusTip('Block IP')
        blockIPAction.triggered.connect(self.blockIPAddress)

        # help

        authorsAction = QAction(QIcon('ikona'), '&Authors', self)
        #authorsAction.setShortcut('Ctrl+A')
        authorsAction.setStatusTip('Show authors')
        authorsAction.triggered.connect(self.credits)

        

        menubar = self.menuBar()

        # connection tab
        connectionMenu = menubar.addMenu('&Connection')
        connectionMenu.addAction(connectAction)
        connectionMenu.addAction(disconnectAction)
        connectionMenu.addAction(exitChannel)
        connectionMenu.addAction(exitAction)

        # administration tab
        adminMenu = menubar.addMenu('&Administration')
        adminMenu.addAction(addChannelAction)
        adminMenu.addAction(delChannelAction)
        adminMenu.addAction(blockNickAction)
        adminMenu.addAction(blockIPAction)

        # help tab
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(authorsAction)


        # -------------   MIDDLE    ---------------------
        middle = QWidget()  # srodkowy widget
        grid = QGridLayout()  # layout srodkowego widgetu

        # Channels - layout and settings
        k_ = QLabel("Channels")
        k_.setMaximumHeight(30)
        grid.addWidget(k_,0,0)
        self.channelsGroupFrame = QFrame()
        self.channelsGroupFrame.setStyleSheet("background-color: #D6D6D6; border: 1px solid black; border-radius: 10px;")

        channelsGroupLayout = QVBoxLayout()
        self.channelsTree = QTreeWidget()
        self.channelsTree.setStyleSheet("background: #D6D6D6; font-size: 18px; border: none;")
        self.channelsTree.setHeaderHidden(True)
        self.channelsTree.itemDoubleClicked.connect(self.enterChannel)
        
        channelsGroupLayout.addWidget(self.channelsTree)
        self.channelsGroupFrame.setLayout(channelsGroupLayout)
        grid.addWidget(self.channelsGroupFrame,1,0)

        # Users - layout and settings
        u_ = QLabel("Users")
        u_.setMaximumHeight(30)
        grid.addWidget(u_,0,1)
        self.usersGroupFrame = QFrame()
        self.usersGroupFrame.setStyleSheet("background-color: #D6D6D6; border: 1px solid black; border-radius: 10px;")

        usersGroupLayout = QVBoxLayout()
        self.usersTree = QTreeWidget()
        self.usersTree.setStyleSheet("background: #D6D6D6; font-size: 18px; border: none; color: green;")
        self.usersTree.setHeaderHidden(True)
        self.usersTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usersTree.connect(self.usersTree, SIGNAL("customContextMenuRequested(QPoint)" ), self.userTreeContextMenu)
        #self.usersTree.setEditTriggers(self.usersTree.NoEditTriggers) ???
        #self.usersTree.setDisabled(True)

        usersGroupLayout.addWidget(self.usersTree)
        self.usersGroupFrame.setLayout(usersGroupLayout)
        grid.addWidget(self.usersGroupFrame,1,1)


        self.myip_ = QLabel("Local IP address:")
        self.myip_.setMaximumHeight(30)
        grid.addWidget(self.myip_, 3, 0)

        self.servip_ = QLabel("Server IP address:")
        self.servip_.setMaximumHeight(30)
        grid.addWidget(self.servip_, 3, 1)


        middle.setLayout(grid)
        self.setCentralWidget(middle)


        # -------------   STATUSBAR  --------------------
        self.statusBar().showMessage('Not connected')

        self.global_variables()
        self.test()
        self.show()

    
    def global_variables(self):
        self.CHANNELS_LIST = []
        self.USERS_LIST = []

    '''def keyPressEvent(self, e):
        print("czesc")
        if e.key() == Qt.Key_Escape:
            self.close()'''

    def test(self):
        self.CHANNELS_LIST = ["Muzyka","Informatyka","Fotografia","Jazda konna"]
        self.USERS_LIST = ["Jacek","Wacek","Justyna"]

    # --------------------------    Auxiliary functions      -------------------------------
    def refresh_channels_tree(self):
        self.channelsTree.clear()
        for i in self.CHANNELS_LIST:
            tmp = QTreeWidgetItem()
            tmp.setText(0, str(i))
            self.channelsTree.addTopLevelItem(tmp)

    def refresh_users_tree(self):
        self.usersTree.clear()
        for i in self.USERS_LIST:
            tmp = QTreeWidgetItem()
            tmp.setText(0, str(i))
            self.usersTree.addTopLevelItem(tmp)

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


    # --------------------------    Connection - EVENTS      -------------------------------

    def connectToServer(self):
        # run from Menu->Polacz
        # connect to server with given IP address, port and unique nick
        tmp = dialogs.ConnectDialog(self)
        if tmp.exec_():
            self.servip_.setText("Server IP address: %s" % tmp.server_ip_address.text())
            self.myip_.setText("Local IP address: %s" % tmp.my_ip_address.currentText())
            print(u"Łącze z serwerem :P")

            self.refresh_channels_tree()

            self.statusBar().showMessage('Connected')

    def disconnectFromServer(self):
        print(u"Rozłączam od serwera :P")
        self.channelsTree.clear()
        self.usersTree.clear()
        self.servip_.setText("Server IP address:")
        self.myip_.setText("Local IP address:")
        self.statusBar().showMessage('Disconnected')

    def exitFromChannel(self):
        self.channelsTree.clear()
        self.usersTree.clear()
        self.statusBar().showMessage('Exited from channel')


    def enterChannel(self, item, column):
        print(u"--- Rozłączenie z poprzednim kanałem")  # TODO: czy wgl w jakims kanale byl
        password, result = QInputDialog.getText(self, 'Password for channel', 'Enter password:')
        if result:
            print(password)
            self.refresh_users_tree()
            


    def quit(self):
        self.disconnectFromServer() # TODO: jakas zmienna sprawdzajaca czy poprawnie rozlaczono z serwerem
        exit()


    def userTreeContextMenu(self, position):
        # for context menu - right click on user in users tree
        # if usersTree has values
        if self.usersTree.topLevelItemCount()>0:
            self.listMenu = QMenu()
            menu_item = self.listMenu.addAction("print nick")
            menu_item.triggered.connect(self.userTreeMenu)
            parent_position = self.usersTree.mapToGlobal(QPoint(0, 0))        
            self.listMenu.move(parent_position + position)
            self.listMenu.show()

    def userTreeMenu(self):
        print(self.usersTree.currentItem().text(0)) # ??? jeszcze nie wiem czemu dziala z zerem


    # ---------------------------     Administration - EVENTS     -------------------------------

    def addChannel(self):
        tmp = dialogs.AddChannelDialog(self)
        if tmp.exec_():
            self.CHANNELS_LIST.append(tmp.name.text())
            print(u"Dodanie kanału ", tmp.name.text(), u" z hasłem ", tmp.password.text())
            self.refresh_channels_tree()

    def delChannel(self):
        channel, result = QInputDialog.getItem(self, "Delete channel", "Name", self.CHANNELS_LIST, 0, False)
        if result:
            try:
                 del self.CHANNELS_LIST[self.CHANNELS_LIST.index(channel)]
                 print("Usunięto ", channel)
                 self.refresh_channels_tree()
            except:
                print(u"Nie ma takiego kanału.")

    def blockNick(self):
        nick, result = QInputDialog.getText(self, 'Block nickname', 'Type nickname:')
        if result:
            print(u"Zablokowano nick ", nick)

    def blockIPAddress(self):
        # TODO: ograniczenie dlugosci wpisywanego tekstu
        ip_address, result = QInputDialog.getText(self, 'Block IP address', 'Type IP address:')
        if result:
            if self.validate_ipv4(ip_address):
                print(u"Zablokowano adres IP ", ip_address)
            else:
                print(u"Błędny adres IPv4")

    #  ----------------------    HELP - EVENTS     -------------------------------

    def credits(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Authors")
        msg.setText(u"Krzysztof Łuczak <br/> Maciej Marciniak")
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