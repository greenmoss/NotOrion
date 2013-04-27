import random

class WormHoles(object):
    def __init__(self, amount, stars):
        self.stars = stars
        self.list = []
        self.generate(amount)

    def generate(self, amount):
        star_indexes = range(len(self.stars.list))
        for repeat in range(amount):
            index1 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
            index2 = star_indexes.pop(random.randint(0, len(star_indexes)-1))

            self.list.append(WormHole(self.stars.list[index1], self.stars.list[index2]))

class WormHole(object):
    """Wormholes are a special class of object; they have no mass and can not exist independently of their endpoint stars."""

    def __init__(self, star1, star2):
        if star1.worm_hole or star2.worm_hole:
            raise Exception, "wormhole endpoint stars may only be used once"

        self.endpoints = (star1, star2)
        star1.worm_hole = self
        star2.worm_hole = self

        self.star1 = star1
        self.star2 = star2
