from fileinput import lineno
from time import sleep
import keyboard
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.parse




def click_button(buttons, name):
    time.sleep(0.7)
    for button in buttons:
        print(button.accessible_name)
        if button.accessible_name == name:
            button.click()
            return

# return [commander name, name list, bracket]
def get_moxfield_decklist(driver, link):
    driver.get(link)

    time.sleep(0.5)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    click_button(buttons, 'Accept')
    time.sleep(0.25)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    click_button(buttons, 'Accept All')

    # Locate the element with the id "commander-bracket-3"
    text = driver.page_source
    try:
        bracklist = int(text.split('commander-bracket-')[1][0])
    except:
        bracklist = 2


    more_button = driver.find_element(By.ID, "subheader-more")

    # Optionally, scroll into view before clicking (if necessary)
    driver.execute_script("arguments[0].scrollIntoView();", more_button)

    # Click the button
    more_button.click()


    # Find the "Export" button by its class and text and click it
    export_button = driver.find_element(By.XPATH, "//a[@class='dropdown-item cursor-pointer no-outline' and text()='Export']")
    export_button.click()

    links = driver.find_elements(By.CSS_SELECTOR, "a.text-body")
    name_list = []
    # Loop through each link and print its text (or any other attribute you want)
    for link in links:
        text = link.text
        if len(text) > 1 and '(' not in text:
            name_list.append(text)
    return  [name_list[0], name_list[1:], bracklist]

def get_top_commanders():
    top_commanders = '''Atraxa, Praetors' Voice
The Ur-Dragon
Edgar Markov
Krenko, Mob Boss
Sauron, the Dark Lord
Yuriko, the Tiger's Shadow
Lathril, Blade of the Elves
Kaalia of the Vast
Kenrith, the Returned King
Miirym, Sentinel Wyrm
Pantlaza, Sun-Favored
Nekusar, the Mindrazer
Gishath, Sun's Avatar
Giada, Font of Hope
Isshin, Two Heavens as One
Wilhelt, the Rotcleaver
Aragorn, the Uniter
Esika, God of the Tree
Shorikai, Genesis Engine
Jodah, the Unifier
Arcades, the Strategist
Chatterfang, Squirrel General
Frodo, Adventurous Hobbit // Sam, Loyal Attendant
Zhulodok, Void Gorger
Animar, Soul of Elements
Muldrotha, the Gravetide
Rin and Seri, Inseparable
Teysa Karlov
The Wise Mothman
Ghyrson Starn, Kelermorph
Korvold, Fae-Cursed King
Meren of Clan Nel Toth
Sidar Jabari of Zhalfir
Atla Palani, Nest Tender
Hakbal of the Surging Soul
Tom Bombadil
Go-Shintai of Life's Origin
Eriette of the Charmed Apple
Henzie "Toolbox" Torre
Niv-Mizzet, Parun
K'rrik, Son of Yawgmoth
Atraxa, Grand Unifier
Breya, Etherium Shaper
Omnath, Locus of All
Urtet, Remnant of Memnarch
Voja, Jaws of the Conclave
Urza, Chief Artificer
Ulalek, Fused Atrocity
Omnath, Locus of Creation
Urza, Lord High Artificer
Thalia and The Gitrog Monster
Kinnan, Bonder Prodigy
Queen Marchesa
Oloro, Ageless Ascetic
Zaxara, the Exemplary
Mr. House, President and CEO
Prosper, Tome-Bound
Captain N'ghathrod
Sisay, Weatherlight Captain
The Necrobloom
Alela, Artful Provocateur
Baylen, the Haymaker
Xyris, the Writhing Storm
Magda, Brazen Outlaw
Lord of the Nazgûl
Tivit, Seller of Secrets
The First Sliver
Anikthea, Hand of Erebos
Alela, Cunning Conqueror
Shelob, Child of Ungoliant
Obeka, Splitter of Seconds
Tovolar, Dire Overlord
Zur the Enchanter
Be'lakor, the Dark Master
Magus Lucea Kane
Sythis, Harvest's Hand
Valgavoth, Harrower of Souls
Ms. Bumbleflower
Aesi, Tyrant of Gyre Strait
Najeela, the Blade-Blossom
Marneus Calgar
The Scarab God
Satoru Umezawa
Caesar, Legion's Emperor
Kykar, Wind's Fury
Hylda of the Icy Crown
Bello, Bard of the Brambles
Narset, Enlightened Exile
Yarok, the Desecrated
Flubs, the Fool
Ezio Auditore da Firenze
Morophon, the Boundless
Feather, the Redeemed
Shalai and Hallar
Dihada, Binder of Wills
Marchesa, the Black Rose
Stella Lee, Wild Card
Ojer Axonil, Deepest Might
Winota, Joiner of Forces
Éowyn, Shieldmaiden
Galadriel, Light of Valinor
Fynn, the Fangbearer
Liesa, Shroud of Dusk
Kibo, Uktabi Prince
Tergrid, God of Fright
Etali, Primal Conqueror
Ygra, Eater of All
Sheoldred, the Apocalypse
Lord Windgrace
Marrow-Gnawer
Rowan, Scion of War
Ob Nixilis, Captive Kingpin
Jetmir, Nexus of Revels
Sefris of the Hidden Ways
Ramos, Dragon Engine
Arabella, Abandoned Doll
Brimaz, Blight of Oreskos
Veyran, Voice of Duality
Brago, King Eternal
Slimefoot and Squee
Brenard, Ginger Sculptor
Judith, Carnage Connoisseur
Light-Paws, Emperor's Voice
Hashaton, Scarab's Fist
Zinnia, Valley's Voice
Ziatora, the Incinerator
Kynaios and Tiro of Meletis
Aminatou, Veil Piercer
Jon Irenicus, Shattered One
Storm, Force of Nature
The Mycotyrant
Hazezon, Shaper of Sand
Derevi, Empyrial Tactician
Goro-Goro and Satoru
Rocco, Street Chef
Varina, Lich Queen
Jodah, Archmage Eternal
Satya, Aetherflux Genius
Glarb, Calamity's Augur
Dina, Soul Steeper
Raffine, Scheming Seer
Zedruu the Greathearted
Rakdos, Lord of Riots
Zimone and Dina
Inalla, Archmage Ritualist
Grand Arbiter Augustin IV
Zada, Hedron Grinder
Omo, Queen of Vesuva
Volo, Guide to Monsters
Syr Gwyn, Hero of Ashvale
Obeka, Brute Chronologist
Haldan, Avid Arcanist // Pako, Arcane Retriever
Talion, the Kindly Lord
Arahbo, Roar of the World
Chulane, Teller of Tales
Azlask, the Swelling Scourge
Orvar, the All-Form
Clavileño, First of the Blessed
Omnath, Locus of Rage
Nicol Bolas, the Ravager
Myrkul, Lord of Bones
Kess, Dissident Mage
Mishra, Eminent One
Kalamax, the Stormsire
Imodane, the Pyrohammer
Raggadragga, Goreguts Boss
Saruman, the White Hand
Braids, Arisen Nightmare
Disa the Restless
Nahiri, Forged in Fury
Skullbriar, the Walking Grave
Yurlok of Scorch Thrash
Gonti, Canny Acquisitor
Chishiro, the Shattered Blade
Kraum, Ludevic's Opus // Tymna the Weaver
Minsc & Boo, Timeless Heroes
Edward Kenway
Adrix and Nev, Twincasters
Yidris, Maelstrom Wielder
Sliver Overlord
Helga, Skittish Seer
Omnath, Locus of Mana
Thrasios, Triton Hero // Tymna the Weaver
Sidisi, Brood Tyrant
Queza, Augur of Agonies
Elesh Norn, Mother of Machines
Zimone, Mystery Unraveler
Imotekh the Stormlord
Ixhel, Scion of Atraxa
Sméagol, Helpful Guide
Okaun, Eye of Chaos // Zndrsplt, Eye of Wisdom
Anowon, the Ruin Thief
Phenax, God of Deception
Elas il-Kor, Sadistic Pilgrim
Marina Vendrell
Commodore Guff
Kadena, Slinking Sorcerer
Ezuri, Claw of Progress
Athreos, God of Passage
Ghave, Guru of Spores
Hinata, Dawn-Crowned
Wick, the Whorled Mind
Ellivere of the Wild Court
Tatyova, Benthic Druid
Mirko, Obsessive Theorist
Faldorn, Dread Wolf Herald
Millicent, Restless Revenant
Ovika, Enigma Goliath
The Gitrog Monster
Ardenn, Intrepid Archaeologist // Rograkh, Son of Rohgahh
Captain America, First Avenger
Ivy, Gleeful Spellthief
Rocco, Cabaretti Caterer
Tiamat
Maelstrom Wanderer
Marwyn, the Nurturer
Aminatou, the Fateshifter
Ayula, Queen Among Bears
Myrel, Shield of Argive
Zethi, Arcane Blademaster
Tayam, Luminous Enigma
Yargle and Multani
The Mimeoplasm
Umbris, Fear Manifest
Anhelo, the Painter
Jhoira, Weatherlight Captain
Nethroi, Apex of Death
Alesha, Who Smiles at Death
Child of Alara
Tasigur, the Golden Fang
Hazel of the Rootbloom
Gargos, Vicious Watcher
Strefan, Maurer Progenitor
Grist, the Hunger Tide
Ratadrabik of Urborg
Kozilek, the Great Distortion
Bilbo, Birthday Celebrant
Narset, Enlightened Master
Slicer, Hired Muscle
Solphim, Mayhem Dominus
Tatsunari, Toad Rider
Admiral Brass, Unsinkable
The Locust God
Wolverine, Best There Is
Nine-Fingers Keene
Indoraptor, the Perfect Hybrid
Codie, Vociferous Codex
Koma, Cosmos Serpent
Saskia the Unyielding
Rashmi and Ragavan
Indominus Rex, Alpha
Eluge, the Shoreless Sea
Admiral Beckett Brass
Kumena, Tyrant of Orazca
Reaper King
Toxrill, the Corrosive
Lynde, Cheerful Tormentor
Shirei, Shizo's Caretaker
Gev, Scaled Scorch
Ghalta, Primal Hunger
Elenda, the Dusk Rose
Karumonix, the Rat King
Morska, Undersea Sleuth
Minn, Wily Illusionist
Juri, Master of the Revue
Dogmeat, Ever Loyal
Talrand, Sky Summoner
Tuvasa the Sunlit
Xavier Sal, Infested Captain
The Gitrog, Ravenous Ride
Xenagos, God of Revels
Yawgmoth, Thran Physician
The Jolly Balloon Man
Galea, Kindler of Hope
Karador, Ghost Chieftain
Kyler, Sigardian Emissary
Extus, Oriq Overlord
The Infamous Cruelclaw
Yuma, Proud Protector
Grolnok, the Omnivore
Prossh, Skyraider of Kher
Osgir, the Reconstructor
Baba Lysaga, Night Witch
Kwain, Itinerant Meddler
Doran, the Siege Tower
Jinnie Fay, Jetmir's Second
Bruvac the Grandiloquent
Bria, Riptide Rogue
Don Andres, the Renegade
Sen Triplets
Selvala, Heart of the Wilds
Brudiclad, Telchor Engineer
Kardur, Doomscourge
Maarika, Brutal Gladiator
The Beamtown Bullies
Tasha, the Witch Queen
Vren, the Relentless
Vihaan, Goldwaker
Gluntch, the Bestower
Gisa and Geralf
Abaddon the Despoiler
Roxanne, Starfall Savant
Ayara, First of Locthwain
Lathiel, the Bounteous Dawn
Tinybones, Trinket Thief
Coram, the Undertaker
Kiora, Sovereign of the Deep
Ognis, the Dragon's Lash
Arna Kennerüd, Skycaptain
Rendmaw, Creaking Nest
Mizzix of the Izmagnus
Greasefang, Okiba Boss
Dr. Madison Li
Shilgengar, Sire of Famine
Kelsien, the Plague
Vishgraz, the Doomhive
Slimefoot, the Stowaway
Kudo, King Among Bears
The Mindskinner
Hapatra, Vizier of Poisons
Karametra, God of Harvests
Riku of Two Reflections
Anje Falkenrath
Pramikon, Sky Rampart
Massacre Girl, Known Killer
Heliod, the Radiant Dawn
Aragorn, King of Gondor
Krark, the Thumbless // Sakashima of a Thousand Faces
Alania, Divergent Storm
Imoti, Celebrant of Bounty
Will, Scion of Peace
Syr Konrad, the Grim
Trostani, Selesnya's Voice
Zurgo Helmsmasher
Ruric Thar, the Unbowed
Azusa, Lost but Seeking
The Tenth Doctor // Rose Tyler
Karn, Legacy Reforged
Urabrask
Astarion, the Decadent
Otharri, Suns' Glory
Lonis, Cryptozoologist
Aeve, Progenitor Ooze
Narci, Fable Singer
Runo Stromkirk
Sigarda, Font of Blessings
Falco Spara, Pactweaver
Magar of the Magic Strings
Neera, Wild Mage
Emry, Lurker of the Loch
Kasla, the Broken Halo
Agatha of the Vile Cauldron
Jan Jansen, Chaos Crafter
Saruman of Many Colors
Jorn, God of Winter
Elsha of the Infinite
The Master, Multiplied
Temmet, Naktamun's Will
Anim Pakal, Thousandth Moon
Anzrag, the Quake-Mole
Jared Carthalion
Breena, the Demagogue
Kellan, the Kid
Kona, Rescue Beastie
Yennett, Cryptic Sovereign
Davros, Dalek Creator
Vorinclex, Monstrous Raider
Magnus the Red
Norin the Wary
Raphael, Fiendish Savior
Marisi, Breaker of the Coil
Garth One-Eye
Iron Man, Titan of Innovation
Rhys the Redeemed
Karlov of the Ghost Council
Thantis, the Warweaver
Chiss-Goria, Forge Tyrant
Duskana, the Rage Mother
Elminster
Sovereign Okinec Ahau
Goreclaw, Terror of Qal Sisma
Felix Five-Boots
Rafiq of the Many
Zask, Skittering Swarmlord
Niv-Mizzet Reborn
The Howling Abomination
Zur, Eternal Schemer
Emmara, Soul of the Accord
Jarad, Golgari Lich Lord
Rograkh, Son of Rohgahh // Silas Renn, Seeker Adept
Zoraline, Cosmos Caller
Hamza, Guardian of Arashin
Urza, Lord Protector
Averna, the Chaos Bloom
Frodo, Sauron's Bane
Alexios, Deimos of Kosmos
Megatron, Tyrant
Kastral, the Windcrested
Galadriel of Lothlórien
Uril, the Miststalker
Amalia Benavides Aguirre
Winter, Misanthropic Guide
Cazur, Ruthless Stalker // Ukkima, Stalking Shadow
Baru, Wurmspeaker
Baral, Chief of Compliance
Loot, the Key to Everything
Cadira, Caller of the Small
Sauron, Lord of the Rings
Zevlor, Elturel Exile
Nelly Borca, Impulsive Accuser
Gavi, Nest Warden
Zacama, Primal Calamity
Arixmethes, Slumbering Isle
Wayta, Trainer Prodigy
Tetzin, Gnome Champion
Galazeth Prismari
Niv-Mizzet, Visionary
Atarka, World Render
Purphoros, God of the Forge
Firesong and Sunspeaker
Mogis, God of Slaughter
Niko, Light of Hope
Neheb, the Eternal
Gyome, Master Chef
Torbran, Thane of Red Fell
Thrun, Breaker of Silence
Silvar, Devourer of the Free // Trynn, Champion of Freedom
Azami, Lady of Scrolls
Aurelia, the Warleader
Merry, Warden of Isengard // Pippin, Warden of Isengard
Carmen, Cruel Skymarcher
The Master of Keys
Ghired, Conclave Exile
Evelyn, the Covetous
Heliod, Sun-Crowned
Kenessos, Priest of Thassa
Kambal, Profiteering Mayor
The Council of Four
Kamiz, Obscura Oculus
Olivia, Opulent Outlaw
Thrasios, Triton Hero // Vial Smasher the Fierce
Liliana, Heretical Healer
Asmoranomardicadaistinaculdacar
Bright-Palm, Soul Awakener
Marchesa, Dealer of Death
Riku of Many Paths
Clement, the Worrywort
Beluna Grandsquall
Liberty Prime, Recharged
Captain Howler, Sea Scourge
Meria, Scholar of Antiquity
Octavia, Living Thesis
Minthara, Merciless Soul
Burakos, Party Leader // Folk Hero
Delney, Streetwise Lookout
Rakdos, the Muscle
Beledros Witherbloom
Marvo, Deep Operative
Breeches, Brazen Plunderer // Malcolm, Keen-Eyed Navigator
King of the Oathbreakers
Sorin of House Markov
Blim, Comedic Genius
Obuun, Mul Daya Ancestor
Altaïr Ibn-La'Ahad
Laughing Jasper Flint
Owen Grady, Raptor Trainer // Blue, Loyal Raptor
Archelos, Lagoon Mystic
Optimus Prime, Hero
General Ferrous Rokiric
Braids, Conjurer Adept
Grenzo, Dungeon Warden
Shroofus Sproutsire
Ranar the Ever-Watchful
Maha, Its Feathers Night
Progenitus
Gisa, the Hellraiser
Xantcha, Sleeper Agent
Estrid, the Masked
Bristly Bill, Spine Sower
Jin-Gitaxias
Errant and Giada
Balan, Wandering Knight
Graaz, Unstoppable Juggernaut
Esix, Fractal Bloom
Finneas, Ace Archer
Kediss, Emberclaw Familiar // Malcolm, Keen-Eyed Navigator
Mishra, Claimed by Gix
Karona, False God
Rivaz of the Claw
Vadrik, Astral Archmage
Araumi of the Dead Tide
Kruphix, God of Horizons
Carth the Lion
Jhoira of the Ghitu
Rukarumel, Biologist
Mendicant Core, Guidelight
Belbe, Corrupted Observer
Abdel Adrian, Gorion's Ward // Candlekeep Sage
Vito, Thorn of the Dusk Rose
Mabel, Heir to Cragflame
'''
    top_commander_list = []
    for commander in top_commanders.split('\n'):
        top_commander_list.append(commander)
    return top_commander_list
def get_all_decks(commander_name):
    return_dict = {}
    if '//' in commander_name:
        url_end = commander_name.split('//')[0]  # idea for var name Luc
    else:
        url_end = commander_name
    replace_char_dict = {
        'ó': 'o',
        ' ': '-',
        '!': '',
        ',': '',
        '\'': '',
    }
    for char in replace_char_dict:
        url_end = url_end.replace(char, replace_char_dict[char])

    url = f'https://json.edhrec.com/pages/decks/{url_end}.json'.lower()
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for index, key in enumerate(data['table']):
            return_dict[data['table'][index]['urlhash']] = {'price': data['table'][index]['price'], 'tags':data['table'][index]['tags'], 'salt': data['table'][index]['salt']}
    return return_dict
data = get_all_decks('niv-mizzet, parun')
for i in data:
    print(print(i))