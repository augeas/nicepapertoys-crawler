
from csv import DictWriter
from itertools import chain
import json
import sys

def burst(item):
    base = {k: item.get(k) for k in ('profile_id', 'url')}
    base['title'] = item.get('title', item.get('profile_name'))
    if item.get('details') or item.get('attributes'):
        base['url'] = 'https://www.nicepapertoys.com/profile/{}'.format(
            item['profile_id'])
    
    images = {
        im['url']: im['path'].split('/')[-1] for im in item.get('images', [])
        if im['status']=='downloaded'
    }

    yield from [{**base, **{'image_url': im, 'filename': images.get(im, '')}}
        for im in item.get('image_urls', [])]

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        infile = sys.argv[1]
        with open(infile, 'r') as f:
            data = json.loads(f.read())
        outfile = sys.argv[2]
        with open(outfile, 'w') as f:
            writer = DictWriter(
                f, ('profile_id', 'title', 'url', 'image_url',
                'filename')
            )
            writer.writeheader()
            writer.writerows(chain.from_iterable(map(burst, data)))

            
