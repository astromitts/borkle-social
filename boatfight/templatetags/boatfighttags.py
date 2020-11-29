from django import template

from borkle.utils import get_dice_image_path

register = template.Library()

@register.filter
def pdb(item):
    import pdb
    pdb.set_trace()

@register.filter
def boat_orientation_class(boat_orientations, boat_label):
    orientation = boat_orientations.get(boat_label)
    if orientation == 'vertical':
        return 'boat-part_vertical'
    return ''
