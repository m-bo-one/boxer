import os
import json
from itertools import chain


from conf import settings
from utils import get_files_from_dir


def build_manifest():
    manifest_path = os.path.join(settings.ASSETS_PATH, 'manifest.json')

    def _map_builder():
        jsons = (fname for fname in get_files_from_dir(
                 os.path.join(settings.ASSETS_PATH, 'tilesets'))
                 if '.json' in fname)
        return ({
            "id": "tileset-" + fname.split('.')[0],
            "type": "json",
            "src": os.path.join("tilesets", fname)
        } for fname in jsons)

    def _spell_builder():
        jsons = (fname for fname in get_files_from_dir(
                 os.path.join(settings.ASSETS_PATH, 'spells'))
                 if '.png' in fname)
        return ({
            "id": "spell-" + fname.split('.')[0],
            "type": "image",
            "src": os.path.join("spells", fname)
        } for fname in jsons)

    def _image_builder():
        jsons = (fname for fname in get_files_from_dir(settings.ASSETS_PATH)
                 if '.png' in fname)
        return ({
            "id": fname.split('.')[0],
            "type": "image",
            "src": fname
        } for fname in jsons)

    def _spritesheet_builder():
        jsons = (fname for fname in get_files_from_dir(
                 settings.ASSETS_SPRITE_PATH) if '.json' in fname)
        return ({
            "id": fname.split('.')[0],
            "type": "spritesheet",
            "src": "sprites/%s" % fname
        } for fname in jsons)

    def _sound_builder():
        jsons = (fname for fname in get_files_from_dir(
                 settings.ASSETS_SOUND_PATH) if '.ogg' in fname)
        return ({
            "id": fname.split('.')[0],
            "type": "sound",
            "src": "sounds/%s" % fname
        } for fname in jsons)

    with open(manifest_path, 'w') as manifest:
        json.dump({
            "path": settings.ASSETS_URL,
            "manifest": [data for data in chain(_spritesheet_builder(),
                                                _sound_builder(),
                                                _image_builder(),
                                                _spell_builder(),
                                                _map_builder())]
        }, manifest, indent=4)


def update_asset_meta(fpath, speed=0.3):
    with open(fpath) as file:
        data = json.load(file)

    for anim_key, value in data['animations'].iteritems():
        data['animations'][anim_key]['speed'] = speed
    with open(fpath, 'w') as outfile:
        json.dump(data, outfile)


def gif2png(folder_path, sprite=None):
    from gevent import monkey; monkey.patch_all()  # noqa
    import gevent
    from PIL import Image

    threads = []
    directions = ('N', 'E', 'W', 'S', 'NE', 'NW', 'SE', 'SW')
    lfiles = (
        # 'StandAttackHeavyBurst',
        # 'StandAttackHeavySingle',
        # 'StandBreatheHeavy',
        # 'StandWalkHeavy',
        'StandBreathe',
        'StandWalk',
        'StandMagichigh',
        # 'StandAttackThrow',
        'StandBreatheRifle',
        'StandWalkRifle',
        'StandAttackRifleSingle',
        'StandAttackRifleBurst',
        'StandRun',
        'DeathRiddled',
        'DeathExplode',
    )
    nfiles = ["_".join([nfile, d + ".gif"])
              for nfile in lfiles for d in directions]
    files = (os.path.join(_dir, nfile)
             for _dir in os.listdir(folder_path) for nfile in nfiles)
    if sprite:
        files = (f for f in files if sprite in f)

    def gen_png(fname):
        try:
            img_name = os.path.join(folder_path, fname)
            im = Image.open(img_name)
        except IOError:
            print('ERROR: Gif %s not found.' % img_name)
            return

        fdir = fname.split('/')[0]
        fpath = os.path.join(settings.PROJECT_PATH,
                             'tmp/png/%s' % fdir)
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
                    os.path.join(fpath, '%s_%s.png' % (key.split('/')[1],
                                 counter)), 'PNG')
                counter += 1
        except (EOFError, IOError):
            im.close()

    for fname in files:
        thread = gevent.spawn(gen_png, fname)
        threads.append(thread)
    gevent.joinall(threads)
