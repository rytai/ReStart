__author__ = 'Kodex'


class MapData:
    mapBoundaries = (0, 0)
    character_layer = {}
    tile_passable = {}  # (x,y): True if passable
    texture_layer = {}
    item_layer = {}

    _open_tiles_modified = False

    # Keeps track of which tiles have changed.
    dirty_tiles = set()

    def __init__(self, map_boundaries_t):
        """
        :rtype : MapData
        """
        self.mapBoundaries = map_boundaries_t
        self.dirty_tiles = set()
        self.character_layer = {}

    def tile_occupied(self, tile_t):
        """Return occupant, false if not occupied, -1 if out of boundaries"""
        if tile_t in self.character_layer:
            return self.character_layer[tile_t]
        else:
            return False

    def in_boundaries(self, tile_t):
        if -1 < tile_t[0] < self.mapBoundaries[0]:
            if -1 < tile_t[1] < self.mapBoundaries[1]:
                return True
        return False

    def attempt_move(self, layer_name, origin, direction=(0, 0), destination=0, checkonly=False):
        """Attempts to move the entity to the direction provided on the layer"""
        assert origin, (int, int)
        assert direction, (int, int)
        if destination == 0:
            destination = origin[0] + direction[0], origin[1] + direction[1]
        if layer_name == "char":
            # Check if the destination is within boundaries
            if not self.in_boundaries(destination):
                return -1

            # Check if the destination is a wall.
            try:
                if self.tile_passable[destination] is False:
                    return -1
            except KeyError:
                pass

            # Check if there is someone on the spot.
            occupied = self.tile_occupied(destination)
            if occupied:
                return occupied
            elif not occupied:
                try:
                    if not checkonly:
                        self.character_layer[destination] = self.character_layer.pop(origin)
                        self.dirty_tiles.add(origin)
                        self.dirty_tiles.add(destination)
                    return True
                # Human error
                except KeyError:
                    print "Mapdata:AttemptMove: Error: No such key: {} or {}".format(destination, origin)
        # Human error.
        else:
            raise StandardError("No layer named: " + layer_name)

    def tile_is_free(self, tile_t):
        if self.in_boundaries(tile_t):
            if not self.tile_occupied(tile_t):
                try:
                    if self.tile_passable[tile_t] is True:
                        return True
                    else:
                        return False
                except KeyError:
                    return True


    def set_passable_tile(self, tile_x, tile_y, passability):
        assert isinstance(passability, bool)
        self.tile_passable[(tile_x, tile_y)] = passability


    def set_item_on_map(self, item, position):
        """
        :type position: tuple
        :type item: Item
        """
        self.item_layer[position] = item
        self.dirty_tiles.add(position)

    def get_items_on_position(self, position):
        """
        :rtype : Item
        :type position: tuple
        """
        try:
            return self.item_layer[position]
        except:
            return None

    def pop_item_from_position(self, position):
        """

        :rtype : Item
        """
        try:
            item_or_list = self.item_layer.pop(position)
            self.set_tile_dirty(position)
            try:
                return item_or_list[-1]
            except AttributeError:
                return item_or_list
        except KeyError:
            print "mapdata:takeitemfrompos: No item in here."

    def set_character_on_map(self, char, position):
        """
        :type position: tuple
        :type char: Creature
        :rtype : None
        """
        self.character_layer[position] = char
        self.dirty_tiles.add(position)

    def get_character_on_position(self, position):
        """
        :rtype: None or Creature
        :type position: tuple
        """
        try:
            return self.character_layer[position]
        except KeyError:
            return None

    def remove_character_from_position(self, position):
        """

        :rtype : None
        :type char: Creature
        :type position: tuple
        """
        try:
            self.character_layer.pop(position)
            self.dirty_tiles.add(position)
        except KeyError:
            print "mapdata:removeCharError: Key doesn't exist:{}".format(position)

    @property
    def get_characters_on_map(self):
        """

        :rtype : list
        """
        return self.character_layer.values()

    def reset_dirty_tiles(self):
        """

        :rtype : None
        """
        self.dirty_tiles = set()

    @property
    def get_texture_layer(self):
        """

        :rtype : dict
        """
        return self.texture_layer

    @property
    def get_dirty_tile_positions(self):
        """

        :rtype : list
        """
        return self.dirty_tiles


    @property
    def get_item_layer(self):
        """

        :rtype : dict
        """
        return self.item_layer

    @property
    def passable_tiles(self):
        """


        :rtype : [tuple(int,int)]
        """
        return [position for position, boolean in self.tile_passable.iteritems() if boolean == True]

    def set_tile_dirty(self, position):
        self.dirty_tiles.add(position)
