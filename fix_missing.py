
import hashlib
from io import BytesIO
import os
import sys
import time

import pandas as pd
from PIL import Image
import requests
from scrapy.utils.python import to_bytes

from nicepapertoys.settings import IMAGES_STORE, IMAGES_THUMBS

def hash_url(url):
    return '{}.jpg'.format(hashlib.sha1(to_bytes(url)).hexdigest())

def get_image(url):
    try:
        req = requests.get(url)
    except:
        return ''
    if req.status_code != 200:
        return ''
    
    try:
        im = Image.open(BytesIO(req.content))
    except:
        return ''
        
    fname = hash_url(url)
    
    im.save('/'.join([IMAGES_STORE, 'full', fname]))
            
    for name, size in IMAGES_THUMBS.items():
        im.resize(size).save('/'.join([IMAGES_STORE, 'thumbs', name, fname]))
    
    print(url)
    time.sleep(1)
    
    return fname


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        infile = sys.argv[1]
        cat_df = pd.read_csv(infile)
        
        missing = (cat_df.filename.isnull()
            & cat_df.image_url.str.startswith('https://storage.ning.com'))
                
        try:
            os.makedirs('/'.join([IMAGES_STORE, 'full']))
        except:
            pass
        
        for path in ['/'.join([IMAGES_STORE, 'thumbs', k])
            for k in  IMAGES_THUMBS.keys()]:
            try:
                os.makedirs(path)
            except:
                pass
            
        cat_df.loc[missing, 'filename'] = cat_df.loc[missing, 'image_url'].map(
            get_image)
        
        cat_df.to_csv(infile, header=True, index=False)







            
