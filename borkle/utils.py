from django.conf import settings

def get_dice_image_path(dice_value):
    if dice_value == 1:
        src = 'images/dice/1.png'
    elif dice_value == 2:
        src = 'images/dice/2.png'
    elif dice_value == 3:
        src = 'images/dice/3.png'
    elif dice_value == 4:
        src = 'images/dice/4.png'
    elif dice_value == 5:
        src = 'images/dice/5.png'
    elif dice_value == 6:
        src = 'images/dice/6.png'
    else:
        src = 'images/dice/0.png'
    return '{}{}'.format(settings.STATIC_URL, src)
