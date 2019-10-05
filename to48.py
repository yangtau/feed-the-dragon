from PIL import Image


def to70(from_name, to_name):
    '''change size of image'''
    img = Image.open(from_name)
    factor = max(img.size) / 70
    out = img.resize((int(img.size[0]/factor),
                      int(img.size[1]/factor)))
    with open(to_name, 'wb') as f:
        out.save(f)
