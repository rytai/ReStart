import random
import creatures
__author__ = 'Kodex'


def roll_dice(amount_of_dices):
    dice_pool = []
    for dice in range(0, amount_of_dices):
        dice_pool.append(random.randint(1, 10))

    if amount_of_dices == 1:
        return dice_pool[0]
    else:
        return dice_pool


def make_skill_roll(ability, skill):
    dice_pool = roll_dice(ability)
    assert dice_pool[0], int
    step = 0
    for dice in dice_pool:
        if dice <= skill:
            step += dice

    return step, dice_pool


def roll_reactions(creatures_in_combat):  # There may be same fitness and roll. tobefixd
    """
    Takes creatures in combat. Puts them in list of tuples and rolls dices. Then takes only the creatures and puts them
    on a single list.
    :type creatures_in_combat: list(Creature)
    """

    reaction_order_ = []
    assert creatures_in_combat, [creatures.Creature]
    for creature in creatures_in_combat:
        dice = roll_dice(1)
        reaction_order_.append((dice, creature.sheet.fitness, creature))

    reaction_order_.sort()

    reaction_order_ = zip(*reaction_order_)[2]

    return list(reaction_order_)