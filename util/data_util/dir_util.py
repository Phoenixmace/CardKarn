import os
import json
def create_folder_structure(root_folder, folders:dict, default_content="{}", overwrite=False):
    if not os.path.exists(root_folder):
        print(root_folder)
        return False
    if not isinstance(folders, dict):
        return False
    for folder, content in folders.items():

        # create files
        if '.' in folder:
            filepath = os.path.join(root_folder, folder)
            if not os.path.exists(filepath) or overwrite:

                # edit content
                if isinstance(content, str):
                    pass
                elif isinstance(content, dict) or isinstance(content, list):
                    content = json.dumps(content, indent=4)
                else:
                    print(f'invalid content type: {type(content)} for {folder} in {root_folder}')
                    content = default_content
                with open(filepath, 'w') as f:
                    f.write(content)
        # make dirs
        elif isinstance(content, dict):
            if not os.path.exists(os.path.join(root_folder, folder)):
                os.makedirs(os.path.join(root_folder, folder))
            create_folder_structure(os.path.join(root_folder, folder), content, default_content, overwrite)
        else:
            print(f'invalid content type: {type(content)} for {folder} in {root_folder}')
            continue
        continue
    return None




