from random import choice

class Rando(object):
    def update(self, gameinfo):
        # Only send so many  fleet at once
        if len(gameinfo.my_fleets) > 2:
            return

        # check if we can attack
        if gameinfo.my_planets and gameinfo.not_my_planets:
            # select a random dest and src planet
            dest = choice(list(gameinfo.not_my_planets.values()))
            src = choice(list(gameinfo.my_planets.values()))
            # launch new fleet if there is enough ships
            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))