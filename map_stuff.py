import os

import resources
from creatures import NPC
__author__ = 'Kodex'


class MapLoader:
    _MapData = None
    _NPC = None
    map_data_list = []
    current_map = None

    map_data_folder = os.path.join('Resources', 'Levels')

    def __init__(self, _MapData, _NPC):
        """


        :rtype : MapLoader
        :type _NPC: NPC
        """
        self.default_map_name = "map_default.map"
        self._MapData = _MapData
        self._NPC = _NPC

    def load_map_named(self, map_name, resource_loader_inst, inventory_class):

        # Read the file to different variables. data=Lists of lines
        map_size, map_name, map_string_data, entity_string_data = self.load_map_data(map_name)

        # Parse string to simple data, int ID's mainly
        map_layer_tile = self.resolve_map_string_data(map_size, map_string_data)
        map_layer_entities = self.resolve_map_entities_data(entity_string_data)

        new_map_data = self._MapData(map_size)

        assert isinstance(resource_loader_inst, resources.Resource_Loader)
        self.populate_map_tiles(new_map_data, map_layer_tile, resource_loader_inst)

        # Create creature instances. Returns hero position.
        hero_pos = self.populate_map_entities(new_map_data, map_layer_entities, resource_loader_inst, inventory_class)

        self.map_data_list.append(new_map_data)

        self.current_map = new_map_data

        return new_map_data, hero_pos

    def load_default_map(self, resource_loader_inst, inventory_class):
        new_map_data, hero_pos = self.load_map_named(self.default_map_name, resource_loader_inst, inventory_class)
        return new_map_data, hero_pos

    @staticmethod
    def populate_map_tiles(_map_data, _map_layer_tile, resource_loader_instance):

        map_size = _map_data.mapBoundaries

        tilesheet = resource_loader_instance.get_tilesheet

        for x in range(map_size[0]):
            for y in range(map_size[1]):
                tile_type = _map_layer_tile[(x, y)]
                tile_texture, tile_passability = tilesheet[tile_type]

                _map_data.texture_layer[(x,y)] = tile_texture
                _map_data.set_passable_tile(x, y, tile_passability)

    def populate_map_entities(self, map_data, _map_layer_entities, resource_loader_inst, inventory_class):
        assert isinstance(map_data, MapData)
        hero_position = None

        for entity in _map_layer_entities:
            id = entity[0]
            position = entity[1]
            speech_id = entity[2]

            # Hero
            if id == 0:
                hero_position = position
            # NPC
            elif id == 1:  # Thug
                new_surface = resource_loader_inst.load_sprite('thug')
                new_inventory = inventory_class()
                new_npc = NPC(new_surface, inventory_instance=new_inventory)
                new_npc.name = 'Thug'
                new_npc.move(*position)
                new_npc.speech_id = 2
                new_npc.in_combat = True
                map_data.set_character_on_map(new_npc, position)
            elif id == 2:  # Thug-NonAgressive
                new_surface = resource_loader_inst.load_sprite('thug')
                new_inventory = inventory_class()
                new_npc = NPC(new_surface, inventory_instance=new_inventory)
                new_npc.name = 'Thug'
                new_npc.move(*position)
                new_npc.speech_id = 2
                map_data.set_character_on_map(new_npc, position)

        return hero_position

    def resolve_map_entities_data(self, linestring_data):
        entitities_data = []  # id, position(x,y), speech_id
        for line in linestring_data:
            # First value of tree int, is ID
            id_ = int(line[0:3])
            # Second and third values of tree int, are position.
            pos_x = int(line[4:7])
            pos_y = int(line[8:11])
            position = pos_x, pos_y
            # Fourth value of tree int, is default_speech
            speech_id = int(line[12:15])

            entitities_data.append([id_, position, speech_id])

        return entitities_data

    def resolve_map_string_data(self, _map_size, _string_data):
        map_layer_tile = {}

        # string data - Rest of the map file: List of csv strings
        for line in range(_map_size[1]):
            data_string = _string_data[line]
            string_position = 0
            length_of_line = len(data_string)
            for tile_in_line in range(_map_size[0]):
                # Tile Id
                data_bit, string_position = self.read_bits(string_position, data_string, 2)
                map_layer_tile[(tile_in_line, line)] = int(data_bit)

                data_bit, string_position = self.read_bits(string_position, data_string, 1)

                if data_bit == ',':
                    pass
                else:
                    print data_string
                    print map_layer_tile
                    raise RuntimeError()

        return map_layer_tile

    @staticmethod
    def read_bits(_string_position, _from, _amount):
        _data_bit = _from[_string_position:_string_position + _amount]
        _string_position += _amount
        return _data_bit, _string_position

    def load_map_data(self, _map_name):
        map_file_name = os.path.join(self.map_data_folder, _map_name)
        f = open(map_file_name, 'r')

        map_size = f.readline()

        map_size = int(map_size[:2]), int(map_size[3:5])

        map_name = f.readline()

        map_string_data = []
        # Read the map tiles to string_data
        for i in range(0, map_size[1]):
            map_string_data.append(f.readline())

        # Remove newline's
        entity_string_data = [line.replace('\n', '').replace('\r', '') for line in f.readlines()]


        f.close()

        return [map_size, map_name, map_string_data, entity_string_data]

    def save_map(self):
        pass


class MapData:
    mapBoundaries = (0, 0)
    character_layer = {}
    tile_passable = {}  # (x,y): True if passable
    texture_layer = {}
    item_layer = {}

    _open_tiles_modified = False

    # Keeps track of which tiles have changed.
    dirty_tiles = set()

    def __init__(self, map_size):
        """
        :rtype : MapData
        """
        map_boundaries = map_size[0], map_size[1]
        self.mapBoundaries = map_boundaries
        self.character_layer = {}
        self.tile_passable = {}
        self.texture_layer = {}
        self.item_layer = {}

        self._open_tiles_modified = False
        self.dirty_tiles = set()

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

    def get_creatures_around_tile(self, tile_t):
        """

        :rtype: list
        """
        results = []
        tile_x, tile_y = tile_t
        # Loop tiles around given coords.
        for x in [tile_x - 1, tile_x, tile_x + 1]:
            for y in [tile_y - 1, tile_y, tile_y + 1]:
                # Ignore the center tile.
                if x == tile_x and y == tile_y:
                    continue
                creature = self.get_character_on_position((x, y))
                if creature:
                    results.append((tile_x, creature))
        return results


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
            except TypeError:
                return item_or_list
        except KeyError:
            print "mapdata:takeitemfrompos: No item in here."

    def set_character_on_map(self, char, position):
        """
        :type position: tuple
        :type char: Creature
        :rtype : None
        """
        if char is not None:
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

    @property
    def get_map_size(self):
        return self.mapBoundaries