from django import template

from borkle.utils import get_dice_image_path

register = template.Library()

@register.filter
def pdb(item):
    import pdb
    pdb.set_trace()

@register.filter
def dice_image(dice_value):
    return get_dice_image_path(dice_value)

@register.filter
def rules_set(foo):
    rule_set_1 = {
        'Any dice of value 1': {
            'score': 100,
            'example_images': [dice_image(1), ]
        },
        'Any dice of value 5': {
            'score': 50,
            'example_images': [dice_image(5), ]
        },
        'Three ones': {
            'score': 300,
            'example_images': [dice_image(1), dice_image(1), dice_image(1), ]
        },
        'Three twos': {
            'score': 200,
            'example_images': [dice_image(2), dice_image(2), dice_image(2), ]
        },
        'Three threes': {
            'score': 300,
            'example_images': [dice_image(3), dice_image(3), dice_image(3), ]
        },
        'Three fours': {
            'score': 300,
            'example_images': [dice_image(4), dice_image(4), dice_image(4), ]
        },
        'Three fives': {
            'score': 500,
            'example_images': [dice_image(5), dice_image(5), dice_image(5), ]
        },
        'Three sixes': {
            'score': 500,
            'example_images': [dice_image(6), dice_image(6), dice_image(6), ]
        },
        'Straight': {
            'score': 1500,
            'example_images': [dice_image(1), dice_image(2), dice_image(3), dice_image(4), dice_image(5), dice_image(6), ]
        },
        'Flush': {
            'score': 3000,
            'example_images': [dice_image(3), dice_image(3), dice_image(3), dice_image(3), dice_image(3), dice_image(3), ]
        },
        'Five of any kind': {
            'score': 2000,
            'example_images': [dice_image(4), dice_image(4), dice_image(4), dice_image(4), dice_image(4), ]
        },
        'Four of any kind': {
            'score': 2000,
            'example_images': [dice_image(2), dice_image(2), dice_image(2), dice_image(2), ]
        },
        'Three pairs': {
            'score': 2500,
            'example_images': [dice_image(2), dice_image(2), dice_image(4), dice_image(4), dice_image(6), dice_image(6), ]
        },
        'Two triplets': {
            'score': 1500,
            'example_images': [dice_image(3), dice_image(3), dice_image(3), dice_image(5), dice_image(5), dice_image(5), ]
        },
        'Four of a kind and a pair': {
            'score': 1500,
            'example_images': [dice_image(2), dice_image(2), dice_image(4), dice_image(4), dice_image(4), dice_image(4), ]
        },
        'Borkle': {
            'score': 0,
            'example_images': [dice_image(2), dice_image(3), dice_image(3), dice_image(4), dice_image(6), dice_image(6), ]
        }
    }
    return [rule_set_1]
