from collections import defaultdict
from PIL import Image
import xml.etree.cElementTree as et
import json
import os


def resize_img(from_name, to_name, size):
    '''change size of image'''
    img = Image.open(from_name)
    if img.size == size:
        print('the original file is in the size')
        return
    out = img.resize(size)
    with open(to_name, 'wb') as f:
        out.save(f)


def shrink_sprite_image(dir_name):
    '''shrink the sprite image and update the json'''
    files = os.listdir(dir_name)
    for f in files:
        fullpath = os.path.join(dir_name, f)
        if f.endswith('.png'):
            resize_img(fullpath, fullpath, (432, 320))
        if f.endswith('.json'):
            with open(fullpath) as f:
                data = json.load(f)
            for _, frames in data['poses'].items():
                for frame in frames:
                    for k, v in frame.items():
                        v = int(v) // 2
                        frame[k] = v
            with open(fullpath, 'w') as f:
                json.dump(data, f)


def sheet_xml2json(from_name, to_name):
    parser = et.parse(from_name)
    root = parser.getroot()
    res = defaultdict(list)
    for it in root:
        name = it.attrib.pop('name')
        while name[len(name)-1].isnumeric():
            name = name[:-1]
        res[name].append(it.attrib)
    with open(to_name, 'w') as f:
        json.dump(res, f)
