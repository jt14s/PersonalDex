import sys, shelve, random, re, requests, urllib
from operator import itemgetter
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy

class MainWindow(QtWidgets.QMainWindow):
    ''' initialize the main display window that houses all of the components '''
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.statusbar = QtWidgets.QStatusBar()
        self.interface = Interface(self)
        self.setup()

    ''' set all necessary values '''
    def setup(self):
        self.setGeometry(50, 50, 1300, 750)
        self.setFixedSize(1300, 750)
        self.setCentralWidget(self.interface)
        self.setStatusBar(self.statusbar)
        self.show()

    ''' when trying to quit, ask if quitting and then save '''
    def closeEvent(self, event):
        reply = QuitMessage().exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            self.save_data()
            event.accept()
        else:
            event.ignore()

    ''' save user settings '''
    def save_data(self):
        s = shelve.open('pokedex_data')
        s['cardcollection'] = self.interface.card_collection
        s.close()

class QuitMessage(QtWidgets.QMessageBox):
    ''' quit app message '''
    def __init__(self):
        QtWidgets.QMessageBox.__init__(self)
        self.setStyleSheet("background: \#CDFFFF; font-size: 20px;")
        self.setText("Power down PokeDex?")
        self.addButton(self.Yes)
        self.addButton(self.No)

class Interface(QtWidgets.QWidget):
    ''' centar widget that acts as the main layout '''
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.pokedex_data = None
        self.card_collection = None
        self.load_dex()
        self.dex_num = len(self.card_collection)
        self.setup()

    ''' setup the left and right tabs '''
    def setup(self):
        ''' Sets up the widget. There are two sides of the screen
            and each one is inside of a parent layout '''
        self.statusMessage = QtWidgets.QLabel(str(self.dex_num) + '/' + str(len(self.pokedex_data.keys())) + ' in collection')
        self.parent.statusbar.insertPermanentWidget(0, self.statusMessage)

        self.left_tab = LeftTab(self)
        self.right_tab = RightTab(self)

        self.parent_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.parent_layout)

        self.left_layout = QtWidgets.QHBoxLayout()
        self.left_layout.addWidget(self.left_tab)

        self.right_layout = QtWidgets.QHBoxLayout()
        self.right_layout.addWidget(self.right_tab)

        self.parent_layout.addLayout(self.left_layout)
        self.parent_layout.addLayout(self.right_layout)

    ''' load all user data on startup '''
    def load_dex(self):
        s = shelve.open('pokedex_data')
        self.pokedex_data = s['pokedata']
        self.card_collection = s['cardcollection']
        s.close()

class LeftTab(QtWidgets.QWidget):
    ''' houses a featured or selected card '''
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent	#interface
        self.setup()

    ''' set up the left tab '''
    def setup(self):
        self.parent_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.parent_layout)

        self.image = FeaturedCard(self)
        self.parent_layout.addWidget(self.image)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_left = Button(self, 'See Featured Card')
        self.button_right = None
        self.button_layout.addWidget(self.button_left)

        self.parent_layout.addLayout(self.button_layout)
        self.button_left.clicked.connect(self.button_clicked)

    def button_clicked(self):
        ''' on featured card button click we want to display info about the card '''
        self.image.tick = False		#stop updating the picture
        self.parent.right_tab.setup_featured()

    ''' back button clicked, set up home again '''
    def back_button_clicked(self):
        if self.parent.right_tab.tab_type == "featured":
            self.parent.parent_layout.removeItem(self.parent.parent_layout.itemAt(1))

        self.image.key = random.choice(list(self.parent.pokedex_data))
        self.image.download_image(self.image.key)

	#reset the featured card ticker
        self.image.display_timer = 60
        self.image.tick = True
        
        #delete the card info box
        self.parent_layout.removeWidget(self.parent.right_tab.box1)
        self.parent.right_tab.box1.deleteLater()
        self.parent.right_tab.box1 = None

        '''Code Description:
                l1: remove the old widget with the now deleted card info box
                l2: remove now empty layout that held l1
                l3: create a fresh layout that will replace l2
                l4: create new widget that will replace l1 and go into l3
                l5: add l4 to l3
                l6: add l3 to parent layout '''
        self.parent.right_layout.removeWidget(self.parent.right_tab)				#l1
        self.parent.parent_layout.removeItem(self.parent.parent_layout.itemAt(1))		#l2
        self.parent.right_layout = QtWidgets.QVBoxLayout()					#l3
        self.parent.right_tab = RightTab(self.parent)						#l4
        self.parent.right_layout.addWidget(self.parent.right_tab)				#l5
        self.parent.parent_layout.addLayout(self.parent.right_layout)				#l6

        # remove second button from buttons layout
        self.button_layout.removeWidget(self.parent.left_tab.button_right)
        self.button_right.deleteLater()
        self.button_right = None

        # update the signal back to home original
        self.button_left.clicked.disconnect()
        self.button_left.setText("See Featured Card")
        self.button_left.clicked.connect(self.button_clicked)

    ''' add or remove card from collection '''
    #this gets called multiple times
    #this is still producing an error in the search tab, doesnt add to collection sometimes
    def collection_action_clicked(self):
        if self.image.key in self.parent.card_collection:
            self.parent.dex_num -= 1
            self.parent.card_collection.remove(self.image.key)
            self.button_right.setText("Add to Collection")

            if self.parent.right_tab.tab_type == "search":
                self.image.image_location = "images/card.png"
                self.image.set_image()
                self.button_right.setStyleSheet("background: gray;")

            if self.parent.right_tab.tab_type == "collection":
                self.parent.right_tab.box1.card_tab.sorted_card_list.pop(self.parent.right_tab.box1.card_tab.currentRow())
                self.button_right.clicked.disconnect()
                self.parent.right_tab.box1.card_tab.takeItem(self.parent.right_tab.box1.card_tab.currentRow())

                self.image.image_location = "images/card.png"
                self.image.set_image()
                self.button_right.setStyleSheet("background: gray;")

        else:
            self.parent.dex_num += 1
            self.parent.card_collection.append(self.parent.left_tab.image.key)
            self.button_right.setText("Remove from Collection")

            if self.parent.right_tab.tab_type == "search":
                self.button_right.setText("Add to Collection")
                self.image.image_location = "images/card.png"
                self.image.set_image()
                self.button_right.setStyleSheet("background: gray;")

        if self.parent.right_tab.tab_type == "search":
            self.parent.right_tab.box1.card_tab.setCurrentRow(self.parent.right_tab.box1.card_tab.currentRow())
            self.button_right.clicked.disconnect()

        self.parent.statusMessage.setText(str(self.parent.dex_num) + '/' + str(len(self.parent.pokedex_data.keys())) + ' in collection')

class FeaturedCard(QtWidgets.QLabel):
    ''' shows a featured or selected card '''
    def __init__(self, parent):
        QtWidgets.QLabel.__init__(self, parent)
        self.parent = parent	#left tab

        #timer stuff
        #swap card every minute
        self.display_timer = 60
        self.timer = QtCore.QTimer()
        self.tick = True
        self.timer.timeout.connect(self.run)
        self.timer.start(1000)

        self.image_location = None
        self.key = random.choice(list(self.parent.parent.pokedex_data))
        self.download_image(self.key)

        self.show()

    ''' ticks timer and updates featured card '''
    def run(self):
        if self.display_timer > 0 and self.tick:
            self.display_timer -= 1
        elif self.tick:
            self.clear()
            self.display_timer = 60
            self.image_loaction = None            
            self.key = random.choice(list(self.parent.parent.pokedex_data))
            self.download_image(self.key)

    ''' uses random key to download image associated with it '''
    def download_image(self, key):
        if '.jpg' in self.parent.parent.pokedex_data[key][6]:
            self.image_location = "images/featuredcard.jpg"
        elif '.png' in self.parent.parent.pokedex_data[key][6]:
            self.image_location = "images/featuredcard.png"
        urllib.request.urlretrieve(self.parent.parent.pokedex_data[key][6], self.image_location)
        self.set_image()

    ''' sets image to featured tab '''
    def set_image(self):
        self.setScaledContents(True)
        image = QtGui.QPixmap(self.image_location)
        image = image.scaled(500, 500)
        self.setPixmap(image)

class RightTab(QtWidgets.QWidget):
    ''' houses a variety of tabs '''
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent	#interface
        self.parent_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.parent_layout)
        self.tab_type = ''
        self.setup_home()

    ''' set up the home widgets '''
    def setup_home(self):
        self.box1 = CollectionTab(self)
        self.box3 = CardSearchTab(self)

        self.parent_layout.addWidget(self.box1)
        self.parent_layout.addWidget(self.box3)

    ''' clear old tabs, load new ones and setup signals '''
    def setup_featured(self):
        self.tab_type = "featured"
        self.clear_tab()

        self.box1 = FeaturedInfo(self)
        self.parent.parent_layout.addStretch(1)
        self.parent_layout.addWidget(self.box1)

        if self.parent.left_tab.image.key in self.parent.card_collection:
            self.parent.left_tab.button_right = Button(self.parent.left_tab, "Remove from Collection")
        else:
            self.parent.left_tab.button_right = Button(self.parent.left_tab, "Add to Collection")

        self.parent.left_tab.button_layout.addWidget(self.parent.left_tab.button_right)

        #connect the new right button signal to action signal
        self.parent.left_tab.button_right.clicked.connect(self.parent.left_tab.collection_action_clicked)
        self.parent.left_tab.button_left.clicked.disconnect()
        self.parent.left_tab.button_left.setText("Back")
        self.parent.left_tab.button_left.clicked.connect(self.parent.left_tab.back_button_clicked)

    ''' on collection tab click, cler tabs, set up new ones and signals '''
    def setup_collection(self, flag = 0):
        if flag == 0:
            self.tab_type = "collection"
        elif flag == 1:
            self.tab_type = "search"

        self.parent.left_tab.image.tick = False
        self.clear_tab()
        self.box1 = CollectionInfo(self, flag)
        self.parent_layout.addWidget(self.box1)

        self.parent.left_tab.button_right = Button(self.parent.left_tab.image, "Add to Collection", 'gray')
        self.parent.left_tab.image.image_location = "images/card.png"
        self.parent.left_tab.image.set_image()
        self.parent.left_tab.button_layout.addWidget(self.parent.left_tab.button_right)

        #disconnect see featured signal
        self.parent.left_tab.button_left.clicked.disconnect()
        self.parent.left_tab.button_left.setText("Back")
        #set back signal
        self.parent.left_tab.button_left.clicked.connect(self.parent.left_tab.back_button_clicked)

    ''' clear all right tab home tabs '''
    def clear_tab(self):
        self.parent_layout.removeWidget(self.box1)
        self.box1.deleteLater()
        self.box1 = None

        self.parent_layout.removeWidget(self.box3)
        self.box3.deleteLater()
        self.box3 = None

class CollectionInfo(QtWidgets.QWidget):
    ''' shows when collection home tab clicked '''
    def __init__(self, parent, flag):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent # right tab
        self.parent_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.parent_layout)

        self.top_layout = QtWidgets.QVBoxLayout()
        self.bottom_layout = QtWidgets.QVBoxLayout()
        top_label = QtWidgets.QLabel("Filter")

        self.filter_tab = FilterTab(self, flag)
        self.card_tab = CardListTab(self, flag)
        self.card_tab.itemPressed.connect(self.card_tab.card_selected)

        self.top_layout.addWidget(top_label)
        self.top_layout.addWidget(self.filter_tab)

        bottom_label = QtWidgets.QLabel("Cards in Collection")
        self.bottom_layout.addWidget(bottom_label)
        self.bottom_layout.addWidget(self.card_tab, 3)

        self.parent_layout.addLayout(self.top_layout, 1)
        self.parent_layout.addLayout(self.bottom_layout, 4)

        self.show()

class FilterTab(QtWidgets.QWidget):
    ''' used to filter cards '''
    def __init__(self, parent, flag):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent #collection info
        self.flag = flag
        self.parent_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.parent_layout)

        self.top_layout = QtWidgets.QHBoxLayout()
        self.mid_layout = QtWidgets.QHBoxLayout()
        self.top_label = QtWidgets.QHBoxLayout()
        self.mid_label = QtWidgets.QHBoxLayout()

        self.top_label.addWidget(QtWidgets.QLabel("Card Name\t\t                Pokemon Type\t\t              Card Type"))
        self.parent_layout.addLayout(self.top_label)

        types = [' ', 'Colorless', 'Darkness', 'Dragon', 'Fairy', 'Fire', 'Fighting', 'Grass', 'Lightning',
                 'Metal', 'Psychic', 'Water']
        self.name_filter = QtWidgets.QLineEdit(self)
        self.type_filter = QtWidgets.QComboBox(self)
        for type in types:
            self.type_filter.addItem(type)

        card_types = [' ', 'Baby', 'Basic', 'Stage 1', 'Stage 2', 'Mega', 'BREAK', 'Level-Up', 'Item', 'Supporter', 'Stadium', 'Basic Energy', 'Special Energy']
        self.card_type_filter = QtWidgets.QComboBox(self)
        for type in card_types:
            self.card_type_filter.addItem(type)

        self.top_layout.addWidget(self.name_filter, 1)
        self.top_layout.addWidget(self.type_filter, 1)
        self.top_layout.addWidget(self.card_type_filter, 1)

        sunmoon = [' ', 'Burning Shadows', 'Guardians Rising', 'Sun and Moon', 'Sun and Moon Promos', ' ']
        xy = ['Evolutions', 'Steam Siege', 'Fates Collide', 'Generations', 'BREAKpoint', 'BREAKtrhough',
              'Ancient Origins', 'Roaring Skies', 'Double Crisis', 'Primal Clash', 'Phantom Forces',
              'Furious Fists', 'Flashfire', 'XY', 'Kalos Starter Set', 'XY Promos', ' ']
        bw = ['Legendary Treasures', 'Plasma Blast', 'Plasma Freeze', 'Plasma Storm', 'Boundaries Crossed',
              'Dragon Vault', 'Dragons Exalted', 'Dark Explorers', 'Next Destinies', 'Noble Victories',
              'Emergin Powers', 'Black and White', 'Black and White Promos', 'McDonalds Collection 2011', 'McDonalds Collection 2012', ' ']
        hgss = ['Call of Legends', 'Triumphant', 'Undaunted', 'Unleashed', 'HeartGold and SoulSilver', 'HeartGold and SoulSilver Promos', 'World Collection', ' ']
        plat = ['Arceus', 'Supreme Victors', 'Rising Rivals', 'Platinum', ' ']
        dp = ['Stormfront', 'Legends Awakened', 'Majestic Dawn', 'Great Encouters', 'Secret WOnders', 'Mysterious Treasures', 'Diamond and Pearl', 'Diamond and Pearl Promos', ' ']
        ex = ['Power Keepers', 'Dragon Frontiers', 'Crystal Guardians', 'Holon Phantoms', 'Legend Makers', 'Delta Species', 'Unseen Forces', 'Emerald', 'Deoxys', 
              'Team Rocket Returns', 'FireRed and LeafGreen', 'Hidden Legends', 'Team Magma vs Team Aqua', 'Dragon', 'Sandstorm', 'Ruby and Sapphire', ' ']
        eser = ['Skyridge', 'Aquapolis', 'Expedition', ' ']
        neo = ['Neo Destiny', 'Neo Revelation', 'Neo Discovery', 'Neo Genesis', ' ']
        gym = ['Gym Challenge', 'Gym Heroes', ' ']
        classic = ['Team Rocket', 'Base Set 2', 'Fossil', 'Jungle', 'Base Set', ' ']
        pop = ['POP Series 1', 'POP Series 2', 'POP Series 3', 'POP Series 4', 'POP Series 5', 'POP Series 6', 'POP Series 7', 'POP Series 8', 'POP Series 9', ' ']
        other = ['Victory Medals', 'Rumble', 'Nintendo Black Star Promos', 'Best of Game', 'Legendary Collection', 'Southern Islands', 'Wizards Black Star Promos', ' ']
        all_sets = [sunmoon, xy, bw, hgss, plat, dp, ex, eser, neo, gym, classic, pop, other]

        self.set_name_filter = QtWidgets.QComboBox(self)
        for set in all_sets:
            for subset in set:
                self.set_name_filter.addItem(subset)

        rarities = [' ', 'Common', 'Uncommon', 'Rare', 'Rare Holo', 'Ultra Rare', 'Secret Rare']
        self.rarity_filter = QtWidgets.QComboBox(self)
        for entry in rarities:
            self.rarity_filter.addItem(entry)

        self.search_button = Button(self, "Search")
        self.search_button.clicked.connect(self.search)
        self.clear_button = Button(self, "Clear")
        self.clear_button.clicked.connect(self.clear_filter)

        self.mid_layout.addWidget(self.set_name_filter, 1)
        self.mid_layout.addWidget(self.rarity_filter, 1)
        self.mid_layout.addWidget(self.search_button, 1)
        self.mid_layout.addWidget(self.clear_button, 1)

        self.parent_layout.addLayout(self.top_layout)
        self.mid_label.addWidget(QtWidgets.QLabel("Set Name\t\t\t      Card Rarity"))
        self.parent_layout.addLayout(self.mid_label)
        self.parent_layout.addLayout(self.mid_layout)

        self.show()

    ''' takes the selected filters, checks the data set, and returns an intersected list of cards found '''
    def search(self):
        self.parent.card_tab.clear()
        name_list = list()
        type_list = list()
        card_list = list()
        set_list = list()
        rarity_list = list()
        all_lists = []

        if self.name_filter.text() != '':
            for card in self.parent.card_tab.cards_in_list:
                if self.name_filter.text() in self.parent.parent.parent.pokedex_data[card][2] or\
                   self.name_filter.text() in self.parent.parent.parent.pokedex_data[card][2].lower():
                    name_list.append(card)
            all_lists.append(name_list)

        if self.type_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.type_filter.currentText() in self.parent.parent.parent.pokedex_data[card][4]:
                    type_list.append(card)
            all_lists.append(type_list)

        if self.card_type_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.card_type_filter.currentText() in self.parent.parent.parent.pokedex_data[card][3]:
                    card_list.append(card)
            all_lists.append(card_list)

        if self.set_name_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.set_name_filter.currentText() in self.parent.parent.parent.pokedex_data[card][1]:
                    set_list.append(card)
            all_lists.append(set_list)

        if self.rarity_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.rarity_filter.currentText() in self.parent.parent.parent.pokedex_data[card][5]:
                    rarity_list.append(card)
            all_lists.append(rarity_list)

        if len(all_lists) != 0:
            filtered_set = set(all_lists[0]).intersection(*all_lists)
        elif len(all_lists) == 0:
            filtered_set = set()

        self.parent.card_tab.cards_in_list = list(filtered_set)
        self.parent.card_tab.load_list(self.parent.card_tab.cards_in_list)

    ''' clears the list of filtered cards '''
    def clear_filter(self):
        self.name_filter.clear()
        self.type_filter.setCurrentIndex(0)
        self.card_type_filter.setCurrentIndex(0)
        self.set_name_filter.setCurrentIndex(0)
        self.rarity_filter.setCurrentIndex(0)

        self.parent.card_tab.clear()
        if self.flag == 0:
            self.parent.card_tab.cards_in_list = self.parent.card_tab.dex_location.card_collection
            self.parent.card_tab.load_list(self.parent.card_tab.dex_location.card_collection)

        elif self.flag == 1:
            self.parent.card_tab.cards_in_list = self.parent.card_tab.dex_location.pokedex_data.keys()
            self.parent.card_tab.load_list(self.parent.card_tab.cards_in_list)

class CardListTab(QtWidgets.QListWidget):
    ''' used to filter cards '''
    def __init__(self, parent, flag):
        QtWidgets.QListWidget.__init__(self, parent)
        self.parent = parent	#collection info

        self.dex_location = self.parent.parent.parent
        if flag == 0:
            self.cards_in_list = self.dex_location.card_collection
        elif flag == 1:
            self.cards_in_list = self.dex_location.pokedex_data.keys()

        self.sorted_card_list = None
        self.load_list(self.cards_in_list)

        self.setCurrentRow(0)
        self.show()

    ''' loads the crad list with data set given '''
    def load_list(self, data):
        #need to sort alphabetically, load data_holder with data needed for sort
        data_holder = list()
        for item in data:
            data_holder.append([self.dex_location.pokedex_data[item][2], self.dex_location.pokedex_data[item][1], item])

        #now that its loaded add the items to the list
        self.sorted_card_list = sorted(data_holder, key=itemgetter(0))
        for card in self.sorted_card_list:
            self.addItem(card[0] + ' -- ' + card[1])

    ''' when card selected update the left tab image '''
    def card_selected(self):
        #self.parent.parent.parent.left_tab.button_right.disconnect()
        self.parent.parent.parent.left_tab.button_right.setStyleSheet("background: \#CDFFFF;")

        #testing this
        self.parent.parent.parent.left_tab.image.key = self.sorted_card_list[self.currentRow()][2]
        self.parent.parent.parent.left_tab.image.download_image(self.parent.parent.parent.left_tab.image.key)

        if self.parent.parent.parent.left_tab.image.key in self.parent.parent.parent.card_collection:
            self.parent.parent.parent.left_tab.button_right.setText("Remove from Collection")
        else:
            self.parent.parent.parent.left_tab.button_right.setText("Add to Collection")

        #once a card has been selected connect the right button
        self.parent.parent.parent.left_tab.button_right.clicked.connect(self.parent.parent.parent.left_tab.collection_action_clicked)

class FeaturedInfo(QtWidgets.QWidget):
    ''' shows featured card data '''
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent	#right tab
        self.setup()

    ''' set up the featured info layout '''
    def setup(self):
        self.parent_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.parent_layout)
        self.setMaximumHeight(170)
        self.setMaximumWidth(570)

        key = self.parent.parent.left_tab.image.key
        data = self.parent.parent.pokedex_data
        self.l1 = InfoLabel(self, data[key][1], 25)
        self.l2 = InfoLabel(self, data[key][2] + ' - ' + data[key][4], 19)
        self.l3 = InfoLabel(self, data[key][3], 19)
        self.l4 = InfoLabel(self, data[key][5], 19)

        self.parent_layout.addWidget(self.l1, 0, QtCore.Qt.AlignTop)
        self.parent_layout.addWidget(self.l2, 0, QtCore.Qt.AlignTop)
        self.parent_layout.addWidget(self.l3, 0, QtCore.Qt.AlignTop)
        self.parent_layout.addWidget(self.l4, 0, QtCore.Qt.AlignTop)

class InfoLabel(QtWidgets.QLabel):
    '''container that featured card info is housed in '''
    def __init__(self, parent, text, txtSize):
        QtWidgets.QLabel.__init__(self, parent)

        self.setMinimumSize(1000, 0)
        self.setMaximumSize(1000, 0)
        self.setMaximumHeight(170)
        self.setMaximumWidth(1000) #570
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        font = "font: {}pt; color: brown;".format(str(txtSize))
        self.setStyleSheet(font)
        self.setText(text)

        self.show()

class CollectionTab(QtWidgets.QWidget):
    ''' collection tab found in home screen '''
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent	#right tab
        self.bg = TabBackground(self, "images/tabbg2.png")

        self.parent_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.parent_layout)

        self.l3 = CustomLabel(self, str(self.parent.parent.dex_num) + '/' + str(len(self.parent.parent.pokedex_data.keys())) + ' in collection')
        self.button = Button(self, "See Collection")
        self.button.clicked.connect(self.button_clicked)

        self.parent_layout.addStretch(1)
        self.parent_layout.addWidget(self.l3)
        self.parent_layout.addStretch(1)
        self.parent_layout.addWidget(self.button)

        self.show()

    ''' detects button clicked '''
    def button_clicked(self):
        self.parent.setup_collection()

class CardSearchTab(QtWidgets.QWidget):
    ''' search tab found in home screen '''
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent	#right tab
        self.bg = TabBackground(self, "images/tabbg1.png")

        self.parent_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.parent_layout)

        self.button = Button(self, "Card Search")
        self.button.clicked.connect(self.button_clicked)
        self.l3 = CustomLabel(self, "Search for Pokemon TCG Cards")

        self.parent_layout.addStretch(1)
        self.parent_layout.addWidget(self.l3)
        self.parent_layout.addStretch(1)
        self.parent_layout.addWidget(self.button)

        self.show()

    ''' takes selected filters and filters all cards and shows the filtered list '''
    def search(self):
        self.parent.card_tab.clear()
        name_list = list()
        type_list = list()
        card_list = list()
        set_list = list()
        rarity_list = list()
        all_lists = []

        if self.name_filter.text() != '':
            for card in self.parent.card_tab.cards_in_list:
                if self.name_filter.text() in self.parent.parent.parent.pokedex_data[card][2]:
                    name_list.append(card)
            all_lists.append(name_list)

        if self.type_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.type_filter.currentText() in self.parent.parent.parent.pokedex_data[card][4]:
                    type_list.append(card)
            all_lists.append(type_list)

        if self.card_type_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.card_type_filter.currentText() in self.parent.parent.parent.pokedex_data[card][3]:
                    card_list.append(card)
            all_lists.append(card_list)

        if self.set_name_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.set_name_filter.currentText() in self.parent.parent.parent.pokedex_data[card][1]:
                    set_list.append(card)
            all_lists.append(set_list)

        if self.rarity_filter.currentText() != ' ':
            for card in self.parent.card_tab.cards_in_list:
                if self.rarity_filter.currentText() in self.parent.parent.parent.pokedex_data[card][5]:
                    rarity_list.append(card)
            all_lists.append(rarity_list)

        if len(all_lists) != 0:
            filtered_set = set(all_lists[0]).intersection(*all_lists)
        elif len(all_lists) == 0:
            filtered_set = set()

        self.parent.card_tab.cards_in_list = list(filtered_set)
        self.parent.card_tab.load_list(self.parent.card_tab.cards_in_list)

    ''' clears the filtered card list '''
    def clear_filter(self):
        self.parent.filter_tab.name_filter.clear()
        self.parent.type_filter.setCurrentIndex(0)
        self.parent.card_type_filter.setCurrentIndex(0)
        self.parent.set_name_filter.setCurrentIndex(0)
        self.parent.rarity_filter.setCurrentIndex(0)

        self.parent.card_tab.clear()
        self.parent.card_tab.cards_in_list = self.parent.card_tab.dex_location.card_collection
        self.parent.card_tab.load_list(self.parent.card_tab.dex_location.card_collection)

    ''' detects button clicked '''
    def button_clicked(self):
        self.parent.setup_collection(1)

class TabBackground(QtWidgets.QLabel):
    ''' used to give a tab a background '''
    def __init__(self, parent, img):
        QtWidgets.QLabel.__init__(self, parent)
        image = QtGui.QPixmap(img)
        self.setPixmap(image)
        self.setScaledContents(True)
        self.show()

class Button(QtWidgets.QPushButton):
    ''' custom button used throughout app '''
    def __init__(self, parent, text, color = '\#CDFFFF'):
        QtWidgets.QPushButton.__init__(self, parent)
        style = "background: " + color + ';'
        self.setStyleSheet(style)
        self.setText(text)
        self.show()

class CustomLabel(QtWidgets.QLabel):
    ''' creates a custum label '''
    def __init__(self, parent, text):
        QtWidgets.QLabel.__init__(self, parent)
        self.setStyleSheet("font-size: 38px; border-radius: 30px; color: white; background-color: rgba(0,0,0,.5); margin-top: 120px; margin-bottom: 120px;")
        self.setText(text)

        self.show()

''' starts the app'''
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    poke_app = MainWindow()
    app.exec_()

