# PersonalDex
Custom made Pokedex application

__Contributors__: Jorge Torres-Aldana  
__Language(s)__: Python  
__Libraries__: BeautifulSoup, PyQt5, requests, shelve, urllib  
__Description__: This application uses a custom programmed scrapper that scrappes https://pkmncards.com/sets/ to gather the data for the pokedex. This takes some time, but it only needs to be run once. Once the data has been scrapped, that data is saved to pokedex_data file(s). You can then run pokedex.py trhough Python and enjoy your very own PersonalDex!

__NOTES__: You must have Python installed on your machine to run this application, as well as PyQt5. I recommend you run the following after installing Python in order to get this application to work. Make sure you are in the correct directories before running the following or it might not work. __These installation instructions are for Windows__   

Installing requests:  
`pip.exe install requets`

Installing PyQt5(Python 3.5 required for this installation method):  
`pip3 install pyqt5`

Once you have those two downloaded go ahead and run:  
`python dex_loader.py`  

This will take ~10 minutes, but after it is done go ahead and run:
`python pokedex.py`

You will see a terminal window, but after a second the applicaton will start. To save your pokedex data simply click the X at the top right of the screen and you will be prompted to power down the pokedex, this saves your data.
