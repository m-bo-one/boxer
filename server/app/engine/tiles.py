import pytmx

from .colliders import spatial_hash


class TiledReader(object):

    @classmethod
    def read_and_add_collision(cls, fname):
        tiled_map = pytmx.TiledMap(fname)
        collision_layers = (layer for layer in tiled_map.layers
                            if isinstance(layer, pytmx.TiledObjectGroup))
        for layer in collision_layers:
            for obj in layer:
                box = cls._get_obj_box(obj)
                spatial_hash.insert_object_for_box(box, obj)

        print(spatial_hash.contents)

    @staticmethod
    def _get_obj_box(obj):
        return {
            'min': (obj.x, obj.y),
            'max': (obj.x + obj.width, obj.y + obj.height)
        }
