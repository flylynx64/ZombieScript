from optparse import OptionParser
import random
import time

import gamelib
from as4 import *

class IGame:
    ''' Abstract class for a game (is-a relationship with derived game). '''

    def __init__(self, max_frames, knobs):
        '''
        Abstract constructor to set up derived game's attributes.

        Args:
            max_frames (int): number of frames to execute game for
        '''
        self._remaining_frames = max_frames
        self._knobs = knobs


    def executeFrame(self):
        ''' Execute the logic for a single frame. Must be overriden. '''
        raise NotImplementedError()

    def loopMain(self):
        ''' Execute game for number of frames specified. Sleep between frames. '''
        while self._remaining_frames > 0:
            self.executeFrame()
            self._remaining_frames -= 1
            time.sleep(self._knobs.sleep_time)

class Map:
    ''' Object that keeps track of all game world state. '''

    def __init__(self, size_x, size_y):
        '''
        Constructor for the map.

        Args:
            size_x (int): width of map
            size_y (int): height of map
        '''
        self._size_x = size_x
        self._size_y = size_y
        self._objects = dict()
        self._current_id = 0

    def generateRandomPlayer(self, health):
        '''
        Generate a random player on the map.

        Args:
            health (int): amount of health player has
        '''
        x, y = self._generateRandomPosition()
        self._objects[self._current_id] = PlayerCharacter(self._current_id, health, x, y, self._getMapView())
        self._current_id += 1

    def generateRandomZombie(self, health):
        '''
        Generate a random zombie on the map.

        Args:
            health (int): amount of health zombie has
        '''
        x, y = self._generateRandomPosition()
        self._objects[self._current_id] = ZombieCharacter(self._current_id, health, x, y, self._getMapView())
        self._current_id += 1

    def getObjectByID(self, obj_id):
        '''
        Get an object by its unique ID.

        Returns:
            ICharacter: object with specified ID; None if ID is invalid
        '''
        if not obj_id in self._objects.keys():
            return None
        return self._objects[obj_id]

    def getIDsByPosition(self, x, y):
        '''
        Get a list of all objects on a position.

        Args:
            x (int): x coordinate of position to check
            y (int): y coordinate of position to check

        Returns:
            list<ICharacter>: objects at the specified position
        '''
        return [obj_item[0] for obj_item in self._objects.items() if obj_item[1].getPos() == (x, y)]

    def getObjects(self):
        '''
        Get a list of all objects on the map.

        Returns:
            list<ICharacter>: list of objects on the map
        '''
        return self._objects.values()

    def getSize(self):
        '''
        Get width and height of map.

        Returns:
            tuple: width (index 0) and height (index 1) of map
        '''
        return self._size_x, self._size_y

    def removeByID(self, obj_id):
        '''
        Remove an object on the map by ID.

        Args:
            obj_id (int): object's ID to be removed
        '''
        self._objects.pop(obj_id)

    def isValidPosition(self, x, y):
        '''
        Check if position is in the bounds of the map.

        Args:
            x (int): x coordinate of position to check
            y (int): y coordinate of position to check

        Returns:
            bool: True if position is in bounds, False otherwise
        '''

        return x >= 0 and x < self._size_x and y >= 0 and y < self._size_y

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        ret = ''

        ret += '-' * (self._size_x + 2)
        ret += '\n'
        for y in range(self._size_y):
            ret += '|'
            for x in range(self._size_x):
                obj_ids = self.getIDsByPosition(x, y)
                if obj_ids:
                    obj_id = min(obj_ids)    # If there are multiple objects, pick the lowest ID
                    obj = self.getObjectByID(obj_id)
                    if isinstance(obj, PlayerCharacter):
                        name = 'P'
                    else:
                        name = 'Z'
                    ret += name
                else:
                    ret += ' '
            ret += '|\n'
        ret += '-' * (self._size_x + 2)
        return ret

    def _generateRandomPosition(self):
        '''
        Private function.
        Generate a random position on the map.

        Returns:
            tuple: random valid x (index 0) and y (index 1) values
        '''
        x = random.randint(0, self._size_x - 1)
        y = random.randint(0, self._size_y - 1)
        return x, y

    def _getMapView(self):
        '''
        Private function.
        Create a MapView object from the map.

        Returns:
            MapView: map attributes as a MapView object.
        '''
        return MapView(self._size_x, self._size_y)

class ZombieHunter(IGame):
    ''' Zombie Hunter game. '''

    def __init__(self, knobs):
        ''' Constructor for Zombie Hunter. '''
        IGame.__init__(self, 100, knobs)
        self._world = Map(15, 15)
        self._world.generateRandomPlayer(1000)
        for i in range(5):
            self._world.generateRandomZombie(100)
        self.heal_count = dict()
        self._knobs = knobs

    def executeFrame(self):
        ''' All the logic for a single frame. '''
        # Get all actions for all characters
        if self._knobs.print_events:
            print('Events')
            print('---')
        events = list()
        for obj in self._world.getObjects():
            if isinstance(obj, ICharacter):
                event = obj.selectBehavior()
                add_event = True

                healing = False
                # If the character is healing, make sure they are allowed to
                if isinstance(event, HealEvent):
                    healing = True
                    if not obj.getID() in self.heal_count.keys():
                        self.heal_count[obj.getID()] = 5
                    if self.heal_count[obj.getID()] <= 0:
                        healing = False
                        add_event = False
                    else:
                        self.heal_count[obj.getID()] -= 1

                if isinstance(event, AttackEvent):
                    valid_ids = [data.getID() for data in obj.getScanResults()]
                    if not event.getTargetID() in valid_ids:
                        add_event = False

                if add_event:
                    events.append(event)
                    if self._knobs.print_events:
                        print(event)

                # If the character is not healing, make it age
                if not healing:
                    event = AgeEvent(obj)
                    events.append(event)
                    if self._knobs.print_events:
                        print(event)

        # Execute actions in proper sequence
        for heal in [event for event in events if isinstance(event, HealEvent)]:
            heal.executeEvent()
        for attack in [event for event in events if isinstance(event, AttackEvent)]:
            attack.executeEvent(self._world)
        for move in [event for event in events if isinstance(event, MoveEvent)]:
            move.executeEvent(self._world)
        for scan in [event for event in events if isinstance(event, ScanEvent)]:
            scan.executeEvent(self._world)
        for age in [event for event in events if isinstance(event, AgeEvent)]:
            age.executeEvent()

        # Remove dead characters
        remove_obj_ids = list()
        for obj in self._world.getObjects():
            if isinstance(obj, ICharacter):
                if obj.getHealth() == 0:
                    remove_obj_ids.append(obj.getID())
        for obj_id in remove_obj_ids:
            if self._knobs.print_events:
                print('{} died!'.format(self._world.getObjectByID(obj_id)))
            self._world.removeByID(obj_id)

        if self._knobs.print_events:
            print('---')

        if self._knobs.print_map:
            print('Map')
            print('---')
            print(self._world)

def main():
    parser = OptionParser()
    parser.add_option('-e', '--no-print-events', dest='print_events', action='store_false', default=True,
                      help='do not display events each frame')
    parser.add_option('-m', '--no-print-map', dest='print_map', action='store_false', default=True,
                      help='do not display the map each frame')
    parser.add_option('-t', '--sleep', dest='sleep_time', type='float', action='store', default=0.5,
                      help='sleep for NUM seconds between frames (float)')
    options, args = parser.parse_args()

    game = ZombieHunter(options)
    game.loopMain()

if __name__ == '__main__':
    main()
