from time import sleep
from .card_class import Card
import csv

def import_collection_from_manabox(file_path, add_lists=False, all_main=False):
    file_path = file_path.replace('\\', '/')
    # get length
    with open(file_path, newline='') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        max_imports =sum(1 for row in csv_data)
    # import each card
    with open(file_path, newline='') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        print(max_imports)
        count = 1
        for row in csv_data:
            if (row[1] == 'binder' or add_lists) and row[2] != 'Name':
                if row[1] == 'deck' or all_main:
                    target = 'main'
                else:
                    target = row[0]
                if row[6] != 'normal':
                    foil = True
                else:
                    foil = False
                try:
                    card = Card(name=row[2], number=row[8], set_code=row[3], foil=foil, language=row[15])
                    card.save_to('bulk', subfolder=target, del_after_save=True)
                    print(f'{round(count / max_imports * 100, 1)}%')
                except:
                    print(row[2], 'could not be loaded')
                sleep(0.05)
                count += 1
