import math

'''
  _   _      _                    ___  _     _           _
 | | | | ___| |_ __   ___ _ __   / _ \| |__ (_) ___  ___| |_ ___
 | |_| |/ _ \ | '_ \ / _ \ '__| | | | | '_ \| |/ _ \/ __| __/ __|
 |  _  |  __/ | |_) |  __/ |    | |_| | |_) | |  __/ (__| |_\__ \
 |_| |_|\___|_| .__/ \___|_|     \___/|_.__// |\___|\___|\__|___/
              |_|                         |__/
Helper Objects
'''

class ScanData:
    ''' The information pertaining to a scanned object at a single location. '''

    def __init__(self, pos, obj_id):
        '''
        Constructor for scan information.

        Args:
            tuple: x (index 0) and y (index 1) position of the object
            obj_id (int): ID of the scanned object
        '''
        self._pos = pos
        self._id = obj_id

    def getPos(self):
        '''
        Get the position of the scanned object.

        Returns:
            tuple: x (index 0) and y (index 1) position of the object
        '''
        return self._pos

    def getID(self):
        '''
        Get the scanned object's ID.

        Returns:
            int: object's ID
        '''
        return self._id

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: scan result formatting as a string
        '''
        return 'ID {} (position: {})'.format(self._id, self._pos)


class MapView:
    ''' An object to keep track of the map attributes. '''
    
    def __init__(self, size_x, size_y):
        '''
        Constructor for map attributes.

        Args:
            size_x (int): width of the map
            size_y (int): height of the map
        '''
        self._size_x = size_x
        self._size_y = size_y

    def getMapSize(self):
        '''
        Get the map size.

        Returns:
            tuple: the width (index 0) and height (index 1) of the map
        '''
        return self._size_x, self._size_y

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

'''
  _____                    _   _
 | ____|_  _____ ___ _ __ | |_(_) ___  _ __  ___
 |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
 | |___ >  < (_|  __/ |_) | |_| | (_) | | | \__ \
 |_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
                    |_|
Exceptions
'''

class IllegalMovementException(RuntimeError):
    ''' An exception type to be raised on an illegal movement. '''

    def __init__(self, init_pos, new_pos):
        '''
        Constructor for exception object.

        Args:
            init_pos (tuple): original position
            new_pos (tuple): new, illegal position
        '''
        self._init_pos = init_pos
        self._new_pos = new_pos

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: exception formatted as a string
        '''
        return 'Illegal movement from {} to {}'.format(self._init_pos, self._new_pos)


'''
  _____                 _
 | ____|_   _____ _ __ | |_ ___
 |  _| \ \ / / _ \ '_ \| __/ __|
 | |___ \ V /  __/ | | | |_\__ \
 |_____| \_/ \___|_| |_|\__|___/

Events
'''


class MoveEvent:
    ''' Event object to specify an object's new position. '''

    def __init__(self, obj, new_x, new_y):
        '''
        Constructor for move event.

        Args:
            obj (ICharacter): the object to move
            new_x (int): new x position for the object
            new_y (int): new y position for the object
        '''
        self._obj = obj
        self._new_pos = int(new_x), int(new_y)

    def executeEvent(self, cur_map):
        '''
        Execute the move event, which will raise an exception if the movement is illegal (see rules below).

        Args:
            cur_map (Map): current world state

        Raises:
            IllegalMovementException: if change in position is greater than 3 units (Manhattan distance) or is out of
                                      bounds on the map
        '''
        old_x, old_y = self._obj.getPos()
        new_x, new_y = self._new_pos
        if abs(old_x - new_x) + abs(old_y - new_y) > 3 or not cur_map.isValidPosition(new_x, new_y):
            raise IllegalMovementException(self._obj.getPos(), self._new_pos)
        self._obj.setPos(new_x, new_y)

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        return '{} moving from {} to {}'.format(self._obj, self._obj.getPos(), self._new_pos)


class HealEvent:
    ''' Event object to specify healing. '''

    def __init__(self, obj):
        '''
        Constructor for the healing event.

        Args:
            obj (ICharacter): the object that is healing
        '''
        self._obj = obj

    def executeEvent(self):
        ''' Execute the heal event. When healing, 25% of the object's initial health is restored.  '''
        self._obj.incrementHealth(self._obj.getInitHealth() * 0.25)

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        return '{} healing'.format(self._obj)


class ScanEvent:
    ''' Event object to perform a scan '''

    def __init__(self, obj):
        '''
        Constructor for the scan event.

        Args:
            obj: object performing the scan
        '''
        self._obj = obj

    def executeEvent(self, cur_map):
        '''
        Execute the scan event. The scan range is circle with 1/4 the area of the map, centered around the object.

        Args:
            cur_map (Map): the current world state
        '''
        pos_x, pos_y = self._obj.getPos()
        size_x, size_y = cur_map.getSize()
        radius = math.sqrt(1.0 / (4.0 * 3.14) * size_x * size_y)

        scan_results = list()
        for scan_obj in cur_map.getObjects():
            # Pass over yourself
            if scan_obj.getID() == self._obj.getID(): continue
            scan_x, scan_y = scan_obj.getPos()
            if math.hypot(pos_x - scan_x, pos_y - scan_y) <= radius:
                scan_results.append(ScanData((scan_x, scan_y), scan_obj.getID()))
        self._obj.setScanResults(scan_results)

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        return '{} scanning'.format(self._obj)


class AttackEvent:
    ''' Event object to specify an attack. '''

    def __init__(self, obj, target_id):
        '''
        Constructor for the attack event.

        Args:
            obj (ICharacter): the object performing the attack
            target_id (int): the ID of the target object
        '''
        self._obj = obj
        self._target_id = target_id

    def executeEvent(self, cur_map):
        '''
        Execute the attack event. The damage dealt is computed as CurrentHealth / e ^ norm(AttackerPos - TargetPos).

        Args:
            cur_map (Map): the current world state
        '''
        obj_pos_x, obj_pos_y = self._obj.getPos()
        target_obj = cur_map.getObjectByID(self._target_id)
        if not target_obj: return
        target_pos_x, target_pos_y = target_obj.getPos()

        dist = math.hypot(obj_pos_x - target_pos_x, obj_pos_y - target_pos_y)
        scale_factor = 1.0 / math.exp(dist)

        target_obj.decrementHealth(self._obj.getHealth() * scale_factor)

    def getTargetID(self):
        '''
        Get the target object's ID

        Returns:
            int: target object's ID
        '''
        return self._target_id

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        return '{} attacking ID {}'.format(self._obj, self._target_id)


class AgeEvent:
    ''' 
    Event object to specify aging. You may emit this in your character if you choose, but the only purpose
    it would serve is to make you lose faster. This event is, however, used by the driver code.
    '''

    def __init__(self, obj):
        '''
        Constructor for the aging event.

        Args:
            obj (ICharacter): the object that is aging
        '''
        self._obj = obj

    def executeEvent(self):
        ''' Execute the aging event. When aging, 2% of the object's initial health is taken.  '''
        self._obj.decrementHealth(self._obj.getInitHealth() * 0.02)

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        return '{} aging'.format(self._obj)


'''
   ____                         ___  _     _           _     ___       _             __
  / ___| __ _ _ __ ___   ___   / _ \| |__ (_) ___  ___| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  ___
 | |  _ / _` | '_ ` _ \ / _ \ | | | | '_ \| |/ _ \/ __| __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \/ __|
 | |_| | (_| | | | | | |  __/ | |_| | |_) | |  __/ (__| |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/\__ \
  \____|\__,_|_| |_| |_|\___|  \___/|_.__// |\___|\___|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___||___/
                                        |__/
Game Object Interfaces
'''

class IScanningObject:
    ''' Abstract class for all objects that can perform a scan (is-a relationship with derived class). '''

    def __init__(self):
        ''' Abstract constructor to set up derived class's scanning attributes. '''
        self._scan_results = list()

    def getScanResults(self):
        '''
        Get the object's latest scanned results.

        Returns:
            list<ScanData>: a list of ScanData objects from the latest scan
        '''
        return self._scan_results

    def setScanResults(self, scan_results):
        '''
        Update the object's latest scanned results.

        Args:
            scan_results (list<ScanData>): a list of the newly scanned data as ScanData objects
        '''
        self._scan_results = scan_results.copy()


class IMovingObject:
    ''' Abstract class for all objects with a position (is-a relationship with derived class). '''

    def __init__(self, x, y, map_view):
        '''
        Abstract constructor to set up derived class's position attributes.

        Args:
            x (int): x position of object
            y (int): y position of object
            map_view (MapView): map properties
        '''
        self._pos = x, y
        self._map_view = map_view

    def getPos(self):
        '''
        Get the object's position.

        Returns:
            tuple: x (index 0) and y (index 1) position of the object
        '''
        return self._pos

    def setPos(self, new_x, new_y):
        '''
        Set the object's position.

        Args:
            new_x (int): new x position for the object
            new_y (int): new y position for the object
        '''
        self._pos = new_x, new_y

    def getMapView(self):
        '''
        Get the map attributes.

        Returns:
            MapView: map attributes
        '''
        return self._map_view


class ILivingObject:
    ''' Abstract class for all objects with health (is-a relationship with derived class). '''

    def __init__(self, health):
        '''
        Abstract constructor to set up derived class's health attributes.

        Args:
            health (int): initial amount of health for the object
        '''
        self._health = health
        self._init_health = health

    def getHealth(self):
        '''
        Get the object's current health.

        Returns:
            int: object's current health
        '''
        return self._health

    def getInitHealth(self):
        '''
        Get the object's initial health.

        Returns:
            int: object's initial health
        '''
        return self._init_health

    def decrementHealth(self, amount):
        '''
        Decrement the object's health. The health has a lower bound of 0.

        Args:
            amount (int): amount to decrement health by
        '''
        self._health = max(self._health - amount, 0)

    def incrementHealth(self, amount):
        '''
        Increment the object's health. The health has an upper bound of its initial health.

        Args:
            amount (int): amount to increment health by
        '''
        self._health = min(self._health + amount, self._init_health)


class ICharacter(IMovingObject, ILivingObject, IScanningObject):
    ''' Abstract class for all characters (is-a relationship with derived class). '''

    def __init__(self, obj_id, health, x, y, map_view):
        '''
        Abstract constructor to set up derived class's character-related attributes.

        Args:
            obj_id (int): object's ID
            health (int): object's initial health
            x (int): x position of object
            y (int): y position of object
            map_view (MapView): map attributes
        '''
        IMovingObject.__init__(self, x, y, map_view)
        ILivingObject.__init__(self, health)
        IScanningObject.__init__(self)
        self._id = obj_id

    def getID(self):
        '''
        Get character's ID.

        Returns:
            int: character's ID
        '''
        return self._id

    def selectBehavior(self):
        ''' Pick a behavior for the character for a single frame by emitting a single event. Must be overriden. '''
        raise NotImplementedError()

    def __str__(self):
        '''
        String conversion for easy reading.

        Returns:
            str: event formatted as a string
        '''
        scan_results = [str(res) for res in self.getScanResults()]
        return 'ID {} (position: {}, health: {}, scan results: {})'.format(self.getID(), self.getPos(),
            self.getHealth(), scan_results)
