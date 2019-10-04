from enum import Enum
import json
import os
import random
import textwrap

fantasy_name_file = "assets/fantasy_name_list.json"

# http://www.roguebasin.com/index.php?title=Markov_chains_name_generator_in_Python
# from http://www.geocities.com/anvrill/names/cc_goth.html
PEOPLE = ['Adara', 'Adena', 'Adrianne', 'Alarice', 'Alvita', 'Amara', 'Ambika', 'Antonia', 'Araceli', 'Balandria', 'Basha',
'Beryl', 'Bryn', 'Callia', 'Caryssa', 'Cassandra', 'Casondrah', 'Chatha', 'Ciara', 'Cynara', 'Cytheria', 'Dabria', 'Darcei',
'Deandra', 'Deirdre', 'Delores', 'Desdomna', 'Devi', 'Dominique', 'Drucilla', 'Duvessa', 'Ebony', 'Fantine', 'Fuscienne',
'Gabi', 'Gallia', 'Hanna', 'Hedda', 'Jerica', 'Jetta', 'Joby', 'Kacila', 'Kagami', 'Kala', 'Kallie', 'Keelia', 'Kerry',
'Kerry-Ann', 'Kimberly', 'Killian', 'Kory', 'Lilith', 'Lucretia', 'Lysha', 'Mercedes', 'Mia', 'Maura', 'Perdita', 'Quella',
'Riona', 'Safiya', 'Salina', 'Severin', 'Sidonia', 'Sirena', 'Solita', 'Tempest', 'Thea', 'Treva', 'Trista', 'Vala', 'Winta']

PLACES = [
    'Booley', 'Nulbilnarg', 'Fiwood', 'Rhine', 'Bacot', 'Meefield', 'Brithimlor', 'Bundushizd',
    'Cafeld', 'Ancleah', 'Camor', 'Cloudshire', 'Arifholm', 'Keliklif', 'Daford', 'Leleah',
    'Herlidalr', 'Strayford', 'Vallinde', 'Glandy', 'Arnilklif', 'Mawre', 'Sturethorp', 'Asheath',
    'Saga', 'Tottori', 'Kochi', 'Shimane', 'Tokushima', 'Yamanashi', 'Fukui', 'Akita',
    'Nara', 'Wakayama', 'Lindorwin', 'Valione', 'Threibluff', 'Anil', 'Penmarth', 'Mastow'
]

PROFESSIONS = [
    'alchemist', 'artist', 'accountant', 'armorer',
    'beekeeper', 'blacksmith', 'barkeeper', 'butcher',  'barber', 'archeologist', 'baker', 'bard',
    'cooper', 'cobbler', 'carpenter', 'computer', 'cartographer', 'chemist',
    'docker', 
    'escort', 'engineer',
    'fisher', 'farmer', 'fiddler', 'fletcher',
    'goldsmith', 'gangster', 'gunsmith',
    'hatter', 'hunter', 'historian', 'healer',
    'inventor',
    'jeweler', 'jester',
    'knight', 'knave',
    'lawyer', 'locksmith', 'laborer',
    'mercenary', 'miller', 'miner', 'mason', 'merchant', 'mechanic',
    'painter', 'professor', 'pilot', 'plumber', 'printer',
    'rancher', 'reaper',
    'sailor', 'soldier', 'silversmith', 'shepherd', 'sawyer', 'scholar',
    'trapper', 'tailor'
]

###############################################################################
# Markov Name model
# A random name generator, by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
# This script is hereby entered into the public domain
###############################################################################
class Mdict:
    def __init__(self):
        self.d = {}

    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            raise KeyError(key)
        
    def add_key(self, prefix, suffix):
        if prefix in self.d:
            self.d[prefix].append(suffix)
        else:
            self.d[prefix] = [suffix]
            
    def get_suffix(self,prefix):
        l = self[prefix]
        return random.choice(l)  

class MName:
    """
    A name from a Markov chain
    """
    def __init__(self, source, chainlen = 2):
        """
        Building the dictionary
        """
        if chainlen > 10 or chainlen < 1:
            print("Chain length must be between 1 and 10, inclusive")
            sys.exit(0)
    
        self.mcd = Mdict()
        oldnames = []
        self.chainlen = chainlen
    
        for l in source:
            l = l.strip()
            oldnames.append(l)
            s = " " * chainlen + l
            for n in range(0,len(l)):
                self.mcd.add_key(s[n:n+chainlen], s[n+chainlen])
            self.mcd.add_key(s[len(l):len(l)+chainlen], "\n")
    
    def New(self):
        """
        New name from the Markov chain
        """
        prefix = " " * self.chainlen
        name = ""
        suffix = ""
        while True:
            suffix = self.mcd.get_suffix(prefix)
            if suffix == "\n" or len(name) > 9:
                break
            else:
                name = name + suffix
                prefix = prefix[1:] + suffix
        return name.capitalize()  

class Sex(Enum):
    NEUTRAL = 0
    FEMALE = 1
    MALE = 2

def get_name():
    return MName(PEOPLE).New()

def get_town_name():
    return MName(PLACES).New()

class Character:
    def __init__(self, last_name=None, alive=random.choice([True, False])):
        self.first_name = get_name()
        # 50% chance to get parent's last name
        if last_name == None:
            self.last_name = get_name()
        else:
            self.last_name = last_name
        # 33% chance to have any sex
        self.sex = Sex(random.randint(0, 2))
        # 50% for parent to be dead by now
        self.alive = alive
        # 10% to not have a home
        if random.random() < .1:
            self.location = None
        else:
            self.location = get_town_name()
        # 5% to not have a profession
        if random.random() < .05:
            self.profession = None
        else:
            self.profession = random.choice(PROFESSIONS)

    @property
    def name(self):
        return self.first_name + " " + self.last_name

class Plot:
    def __init__(self, inspiration=0):
        self.protagonist = Character(alive=True)

        # %20 to be an orphan
        if random.random() < .2:
            self.parent = None
        else:
            # 50% for parent to share last name
            if random.random() < 0.5:
                self.parent = Character()
            else:
                self.parent = Character(last_name=self.protagonist.last_name)
        self.lines = self.get_plot_lines(inspiration)

    def plot_str(self):
        temp_str = "[{}] ".format(self.protagonist.name)
        score = 0
        """
        add 1 if character has parent
        add 2 if character has a birthplace
        add 4 if parent had a profession
        """
        parent_sex = ["parent", "mother", "father"]
        
        if self.parent is not None:
            score += 1
        if self.protagonist.location is not None:
            score += 2
        if self.parent is not None and self.parent.profession is not None:
            score += 4

        if score == 0:
            temp_str += "You were born to unknown parents, in an unknown land."
        elif score == 1:
            temp_str += "You were born to your " + parent_sex[self.parent.sex.value] + " " + self.parent.name + " in an unknown land."
        elif score == 2:
            temp_str += "You were born in " + self.protagonist.location + " to unknown parents."
        elif score == 3:
            temp_str += "You were born to your " + parent_sex[self.parent.sex.value] + " " + self.parent.name + " in " + self.protagonist.location + "."

        elif score == 4:
            temp_str += "You were born to unknown parents, in an unknown land."
        elif score == 5:
            temp_str += "You were born to your " + parent_sex[self.parent.sex.value] + " " + self.parent.name
            if self.parent.profession[0] in ['a', 'e', 'i', 'o', 'u']:
                temp_str += ", an " + self.parent.profession + ", in an unknown land."
            else:
                temp_str += ", a " + self.parent.profession + ", in an unknown land."
                
        elif score == 6:
            temp_str += "You were born in " + self.protagonist.location + " to unknown parents."
        elif score == 7:
            temp_str += "You were born to your " + parent_sex[self.parent.sex.value] + " " + self.parent.name
            if self.parent.profession[0] in ['a', 'e', 'i', 'o', 'u']:
                temp_str += ", an " + self.parent.profession + ", in " + self.protagonist.location + "."
            else:
                temp_str += ", a " + self.parent.profession + ", in " + self.protagonist.location + "."
            
            
        return temp_str

    def get_plot_lines(self, inspiration=0):
        # TODO: make this cleaner, 40 shouldn't be a literal
        plot_lines = textwrap.wrap(self.plot_str(), 40)
        lines = []
        
        for line in plot_lines:
            lines.append(line)

        return lines

    def regen_plot_lines(self, inspiration=0):
        self.lines = self.get_plot_lines()
        
