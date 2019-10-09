from collections import defaultdict
from PIL import Image
import xml.etree.cElementTree as et
import json


def resize_img(from_name, to_name, size):
    '''change size of image'''
    img = Image.open(from_name)
    factor = max(img.size) / size
    out = img.resize((int(img.size[0]/factor),
                      int(img.size[1]/factor)))
    with open(to_name, 'wb') as f:
        out.save(f)


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
