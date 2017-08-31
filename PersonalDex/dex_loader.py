import urllib.request
import re, shelve
from bs4 import BeautifulSoup

class DexLoader:
    def __init__(self):
        self.all_set_links = []
        self.all_pkmn_rows = []

        self.collection = []
        self.pokedex_data = dict()

        page = urllib.request.urlopen("https://pkmncards.com/sets/").read()
        soup = BeautifulSoup(page, "html.parser")
        all_links = soup.find_all("li")

        #get all of the links to the sets
        for set_link in all_links:
            link = re.findall('<a href="(.+?)"', str(set_link), re.S)
            self.all_set_links.append(link[0])
            
    def get_data(self):
        for link in self.all_set_links:
            page = urllib.request.urlopen(link).read()
            soup = BeautifulSoup(page, "html.parser")
            tags = soup.find_all("article")

            for tag in tags:
                self.all_pkmn_rows.append(tag)

    def parse_data(self):
        sunmoon = ['Sun and Moon', '-bus-', '-gri-', '-sum-', '-sun-moon-promos']
        xy = ['XY', '-evo-', '-sts-', '-fco-', '-gen-', '-bkp-', '-bkt-',
              '-aor-', '-ros-', '-dcr-', '-prc-', '-phf-', '-ffi-', '-flf-', '-xy-',
              '-kss-', '-xy-promos-']
        bw = ['Black and White', '-ltr-', '-plb-', '-plf-', '-pls-', '-bcr-', '-drv-',
              '-drx-', '-dark-explorers-', '-nxd-', '-nvi-', '-epo-', '-epo-', '-blw-', '-black-white-promos-',
              '-mcdonalds-collection-2011-', '-mcdonalds-collection-2012-']
        hgss = ['HeartGold and SoulSilver', '-cl-', '-tm-', '-ud-', '-ul-', '-hs-',
                '-heartgold-soulsilver-promos-', '-world-collection-']
        plat = ['Platinum', '-ar-', '-sv-', '-rising-rivals-', '-pl-']
        dp = ['Diamond and Pearl', '-sf-', '-la-', '-md-', '-ge-', '-sw-', '-mt-', '-dp-', '-diamond-pearl-promos-']
        ex = ['EX', '-pk-', '-df-', '-cg-', '-hp-', '-lm-', '-ds-', '-uf-', '-em-', '-dx-', '-team-rocket-returns-',
              '-rg-', '-hl-', '-ma-', '-dr-', '-ss-', '-rs-']
        e = ['E-Card', '-sk-', '-aq-', '-expedition-']
        neo = ['Neo', '-neo-']
        gym = ['Gym', '-gym-challenge-', '-gym-heroes-']
        classic = ['Classic', '-tr-', '-b2-', '-fo-', '-ju-', '-bs-']
        pop = ['POP', '-pop-']
        other = ['Other', '-victory-medals', '-ru-', '-nintendo-black-star-promos-', '-best-of-game-', '-lc-', '-si-',
                 '-wizards-black-star-promos-']

        all_series = [sunmoon, xy, bw, hgss, plat, dp, ex, e, neo, gym, classic, pop, other]
        
        vict_medals_num = 1
        for card_data in self.all_pkmn_rows:
            series_name = ''
            set_name = ''
            pkmn_name = ''
            card_type = ''
            pkmn_type = ''
            rarity = ''
            img_link = ''
            pkmn_link = ''
            pkmn_number = ''

            set_nm = re.findall('.+?"set">(.+?)<', str(card_data), re.S)
            set_name = set_nm[0]
            if '&amp;' in set_name:
                set_name = set_name.replace('&amp;', 'and')
            
            name = re.findall('.+?"name">.+?>(.+?)<', str(card_data), re.S)
            pkmn_name = name[0]
            if '!' in pkmn_name:
                pkmn_name = pkmn_name.replace('!', 'EXC')

            crd_type = re.findall('.+?"card-type">(.+?)<', str(card_data), re.S)
            card_type = crd_type[0]

            pkm_type = re.findall('.+?"pokemon-type">(.+?)<', str(card_data), re.S)
            pkmn_type = pkm_type[0]

            rarity_type = re.findall('.+?"rarity">(.+?)<', str(card_data), re.S)
            rarity = rarity_type[0]

            link = re.findall('"name"><a href="(.+?)"', str(card_data), re.S)
            pkmn_link = link[0]

            #get the image link
            link_page = urllib.request.urlopen(pkmn_link).read()
            soup = BeautifulSoup(link_page, "html.parser")
            img_loc = soup.find_all("div", { "class" : "scan left" })
            img_link = re.findall('href="(.+?)"', str(img_loc[0]), re.S)[0]

            for series in all_series:
                for entry in series[1:]:
                    if entry in pkmn_link:
                        series_name = series[0]
                        break

            if set_name == 'Victory Medals':
                pkmn_number = str(vict_medals_num)
                vict_medals_num += 1
            else:
                pkmn_num = re.findall('.+?"number">(.+?)<', str(card_data), re.S)
                pkmn_number = pkmn_num[0]

                if '!' in pkmn_number:
                    pkmn_number = pkmn_number.replace('!', 'EXC')

            key = set_name.replace(' ', '').lower() + pkmn_number

            #catch single ecard exception
            if key == 'risingrivals97':
                series_name = 'Platinum'
            
            self.pokedex_data[key] = [series_name, set_name, pkmn_name, card_type, pkmn_type, rarity, img_link]
            print(key, self.pokedex_data[key])

    def save_data(self):
        s = shelve.open("pokedex_data")
        s['pokedata'] = self.pokedex_data
        s['cardcollection'] = self.collection
        s.close()

    '''
    def load_data(self):
        s = shelve.open("pokedex_data")
        self.pokedex_data = s['pokedata']
        print(self.pokedex_data)
    '''

if __name__ == '__main__':
    dex = DexLoader()
    print ('checkpoint 1')
    dex.get_data()
    print ('checkpoint 2')
    dex.parse_data()
    print ('checkpoint 3')
    dex.save_data()
    print ('checkpoint 4: done...')
