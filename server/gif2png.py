from gevent import monkey; monkey.patch_all()  # noqa

import sys
import os
import json

import gevent

from PIL import Image

from conf import settings


def get_files_from_dir(path):
    from os import listdir
    from os.path import isfile, join
    return [f for f in listdir(path) if isfile(join(path, f))]


def set_frames_speed(speed=0.3):
    path = sys.argv[1]
    with open(path) as file:
        data = json.load(file)

    for anim_key, value in data['animations'].iteritems():
        data['animations'][anim_key]['speed'] = speed
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def main():
    try:
        folder = sys.argv[1]
    except IndexError:
        print('ERROR: Need specify folder for extraction.')
        return

    threads = []
    # files = get_files_from_dir(folder)
    files = [
        'StandAttackHeavyBurst_N.gif',
        'StandAttackHeavyBurst_E.gif',
        'StandAttackHeavyBurst_W.gif',
        'StandAttackHeavyBurst_S.gif',
        'StandBreatheHeavy_N.gif',
        'StandBreatheHeavy_E.gif',
        'StandBreatheHeavy_W.gif',
        'StandBreatheHeavy_S.gif',
        'StandWalkHeavy_N.gif',
        'StandWalkHeavy_E.gif',
        'StandWalkHeavy_W.gif',
        'StandWalkHeavy_S.gif',
        'StandBreathe_N.gif',
        'StandBreathe_E.gif',
        'StandBreathe_W.gif',
        'StandBreathe_S.gif',
        'StandWalk_N.gif',
        'StandWalk_E.gif',
        'StandWalk_W.gif',
        'StandWalk_S.gif',
        'StandMagichigh_N.gif',
        'StandMagichigh_E.gif',
        'StandMagichigh_W.gif',
        'StandMagichigh_S.gif',
    ]

    def gen_png(fname):
        try:
            img_name = os.path.join(folder, fname)
            im = Image.open(img_name)
        except IOError:
            print('ERROR: Gif %s not found.' % img_name)
            return

        fdir = [fn for fn in folder.split('/') if fn][-1]
        fpath = os.path.join(settings.SERVER_PATH,
                             'extractor/assets/sprites/%s' % fdir)
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        # To iterate through the entire gif
        key, _ = fname.split('.')
        try:
            counter = 0
            while 1:
                im.seek(im.tell()+1)
                pixdata = im.load()

                for y in range(im.size[1]):
                    for x in range(im.size[0]):
                        if pixdata[x, y] == (255, 255, 255, 255):
                            pixdata[x, y] = (255, 255, 255, 0)
                im.save(
                    os.path.join(fpath, '%s_%s.png' % (key, counter)), 'PNG')
                counter += 1
        except EOFError:
            im.close()

    for fname in files:
        thread = gevent.spawn(gen_png, fname)
        threads.append(thread)
    gevent.joinall(threads)


if __name__ == '__main__':
    set_frames_speed()
    # main()
