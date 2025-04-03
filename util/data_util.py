import json
import os



def get_source_folder_path():
    source_folder_name = 'CardKarn'
    file_path = os.getcwd()
    folder_path = file_path[:file_path.index(source_folder_name)+len(source_folder_name)] + os.sep
    return folder_path
def get_data_path(filename, subfolder=False):
    filepath = f'{get_source_folder_path()}data{os.sep}{ int(bool(subfolder))*(str(subfolder) +os.sep)}{filename}'
    if os.path.exists(filepath):
        return filepath
    else:
        print('filepath could not be found: ', filepath)
        return False
