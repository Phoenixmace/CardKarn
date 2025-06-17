import os
import requests
from models.Card import BaseCard
from util import data_util
from PIL import Image
def get_image_path(scryfall_id, version='normal', base='normal'):
    card = BaseCard({'scryfall_id': scryfall_id})
    source_image_path = data_util.get_data_path('images')
    image_name = f'{scryfall_id}_{version}.jpg'
    image_path = source_image_path + os.sep + image_name
    if os.path.exists(image_path):
        return image_path
    else:
        if version == 'pixelated':
            url_version = base
        else:
            url_version = version
        if hasattr(card,'card_faces'):
            if url_version in card.card_faces[0]['image_uris']:
                url = card.card_faces[0]['image_uris'][url_version]
        else:
            if url_version in card.image_uris:
                url = card.image_uris[url_version]
        response = requests.get(url)
        if response.status_code == 200:
            if version == 'pixelated':
                base_image_path = source_image_path + os.sep + f'{scryfall_id}_{base}.jpg'
                with open(base_image_path, 'wb') as f:
                    f.write(response.content)
                img = Image.open(base_image_path)
                # Resize smoothly down to 16x16 pixels
                imgSmall = img.resize((16, 16), resample=Image.Resampling.BILINEAR)
                # Scale back up using NEAREST to original size
                result = imgSmall.resize(img.size, Image.Resampling.NEAREST)

                # Save
                result.save(image_path, quality=95)
                return image_path
            else:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                print("Image downloaded successfully!")

                return image_path
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
            return None

