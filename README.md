# PersonalDex
Custom made Pokedex application

__Contributors__: Jorge Torres-Aldana  
__Language(s)__: Python  
__Libraries__: BeautifulSoup, PyQt5, requests, shelve, urllib  
__Description__: This application uses a custom programmed scrapper that scrappes https://pkmncards.com/sets/ to gather the data for the pokedex. This takes some time, but it only needs to be run once. Once the data has been scrapped, that data is saved to pokedex_data file(s). You can then run pokedex.py trhough Python and enjoy your very own PersonalDex!

__Examples__:
Below I show what the various screens in the application look like. 

Let's begin with the main screen. This screen shows a featured card on the left side of the Screen.This features card is randomly selected from the thousands of cards in the TCG. The card will change every 1 minute, or every time you come back to the main screen. Underneath the featured card is a See featured Card button that will take you to a seperate screen that contains more information about the card and also lets you add or remove said card from your collection. The right side of the screen hosts two additional tabs that allow you to either see your collection, or see a list of every card in the TCG (up to Burning Shadows at the moment). The user collection tab also shows the number of cards in their collection. This number can also be found at the bottom right of the screen of every screen.

![alt text](https://github.com/jt14s/PersonalDex/blob/master/mainScreen.PNG)

The next screen seen here is the featured card screen. As stated previously, it shows more information about the featured card and allows it to be added or removed from the user's collection.

![alt text](https://github.com/jt14s/PersonalDex/blob/master/featuredScreen.PNG)

The next screen is the user's collection screen. This screen displays a list of all cards in the user's collection in alphabetical order. There is also a tab above the list of cards that allows the user to filter cards through a number of different filter types. The filtering is cumulative, which means you can filter once, and then filter the result of the previous filter. Pressing clear will clear all of the filters. The currently selected card is also displayed on the left side tab.

![alt text](https://github.com/jt14s/PersonalDex/blob/master/collectionScreen.PNG)

The final screen is the search cards tab. This tab shows every card in the TCG(up to Burning Shadows currently). The user can then filter the cards like described in the collection tab. This screen behaves much like the collection tab.

![alt text](https://github.com/jt14s/PersonalDex/blob/master/cardsScreen.PNG)

__Insatallation__: You must have Python installed on your machine to run this application, as well as PyQt5. I recommend you run the following after installing Python in order to get this application to work. Make sure you are in the correct directories before running the following or it might not work. __These installation instructions are for Windows__   

Installing requests:  
`pip.exe install requets`

Installing PyQt5(Python 3.5 required for this installation method):  
`pip3 install pyqt5`

Once you have those two downloaded go ahead and run:  
`python dex_loader.py`  

This will take ~10 minutes, but after it is done go ahead and run:
`python pokedex.py`

You will see a terminal window, but after a second the applicaton will start. To save your pokedex data simply click the X at the top right of the screen and you will be prompted to power down the pokedex, this saves your data.
