import random
import math
import numpy

from gamelib import *

class ZombieCharacter(ICharacter):
    def __init__(self, obj_id, health, x, y, map_view):
        ICharacter.__init__(self, obj_id, health, x, y, map_view)

    def selectBehavior(self):
        prob = random.random()

        # If health is less than 50%, then heal with a 10% probability
        if prob < 0.1 and self.getHealth() < self.getInitHealth() * 0.5:
            return HealEvent(self)

        # Pick a random direction to walk 1 unit (Manhattan distance)
        x_off = random.randint(-1, 1)
        y_off = random.randint(-1, 1)

        # Check the bounds
        map_view = self.getMapView()
        size_x, size_y = map_view.getMapSize()
        x, y = self.getPos()
        if x + x_off < 0 or x + x_off >= size_x:
            x_off = 0
        if y + y_off < 0 or y + y_off >= size_y:
            y_off = 0

        return MoveEvent(self, x + x_off, y + y_off)

class PlayerCharacter(ICharacter):
    def __init__(self, obj_id, health, x, y, map_view):
        ICharacter.__init__(self, obj_id, health, x, y, map_view)
        self.scan = 0
        self.healcount = 0
        # You may add any instance attributes you find useful to save information between frames

    def selectBehavior(self):
        # Replace the body of this method with your character's behavior
        if self.scan ==0:
            #Scan
            self.scan = 1
            return ScanEvent(self)
        else:
            closestzdist=99999999
            closestzid=0
            closestzthreshold = 3
            healththresh = 0.4

            map_view = self.getMapView()
            size_x, size_y = map_view.getMapSize()
            x, y = self.getPos()
            xz = 0
            yz = 0            
            
            #Find closest zombie
            for z in self.getScanResults():
                dist=math.sqrt((self.getPos()[0]-z.getPos()[0])**2+(self.getPos()[1]-z.getPos()[1])**2)
                if dist<closestzdist:
                    closestzid=z.getID()
                    xz = z.getPos()[0]
                    yz = z.getPos()[1]
                    closestzdist=dist
            
            #Case when Zombie on same spot as us
            if closestzdist==0 and self.getHealth() < self.getInitHealth() * healththresh:
                self.scan = 0
                self.healcount += 1
                if self.healcount <= 5:
                    return HealEvent(self)
                else:
                    #attack because it should be an instant kill
                    return AttackEvent(self, closestzid)            
            
            #Case when Zombie close to us and Health is high                                      
            if closestzdist<=closestzthreshold and self.getHealth() > self.getInitHealth() * healththresh:
                #Attack closest Zombie
                self.scan = 0
                return AttackEvent(self, closestzid)
            
            #Cases when Zombie close to us and Health is low 
            if  closestzdist<=closestzthreshold and self.getHealth() < self.getInitHealth() * healththresh:
                if self.getHealth() < self.getInitHealth() *healththresh*0.8 and self.healcount <5:
                    self.scan = 0
                    self.healcount += 1
                    return HealEvent(self)
                elif self.getHealth() < self.getInitHealth() *healththresh*0.8 and self.healcount >=5:
                    self.scan = 0
                    return AttackEvent(self, closestzid)                    
                else:
                    xzdiff = x - xz # Diff x coordinate of nearest zombie
                    yzdiff = y - yz # Diff y coordinate of nearest zombie
                    if abs(xzdiff) + abs(yzdiff) >3:
                        if abs(xzdiff)>abs(yzdiff):
                            xzdiff = 2*numpy.sign(xzdiff)
                            if yzdiff == 0:
                                xzdiff = 3
                            yzdiff = 1*numpy.sign(yzdiff)
                        else:
                            xzdiff = 1*numpy.sign(xzdiff)
                            yzdiff = 2*numpy.sign(yzdiff)
                            if xzdiff == 0:
                                yzdiff = 3
                    if x + xzdiff < 0 or x + xzdiff >= size_x:
                        xzdiff = 0
                    if y + yzdiff < 0 or y + yzdiff >= size_y:
                        yzdiff = 0
                    self.scan = 0
                    return MoveEvent(self, x + xzdiff, y + yzdiff) #Moving away from Zombie
                
            #Case when Zombie far from us and We have 2 heals left                     
            if closestzdist>closestzthreshold and self.healcount <=3:
                self.scan = 0
                #Case when health is high
                if self.getHealth() > self.getInitHealth() * healththresh:
                    xzdiff = x - xz # Diff x coordinate of nearest zombie
                    yzdiff = y - yz # Diff y coordinate of nearest zombie
                    if abs(xzdiff) + abs(yzdiff) >3:
                        if abs(xzdiff)>abs(yzdiff):
                            xzdiff = 2*numpy.sign(xzdiff)
                            if yzdiff == 0:
                                xzdiff = 3
                            yzdiff = 1*numpy.sign(yzdiff)
                        else:
                            xzdiff = 1*numpy.sign(xzdiff)
                            yzdiff = 2*numpy.sign(yzdiff)
                            if xzdiff == 0:
                                yzdiff = 3
                    if x + xzdiff < 0 or x + xzdiff >= size_x:
                        xzdiff = 0
                    if y + yzdiff < 0 or y + yzdiff >= size_y:
                        yzdiff = 0
                    return MoveEvent(self, x + xzdiff, y + yzdiff) #Moving away from zombie
                else:
                    self.healcount +=1
                    return HealEvent(self)
                
            # Case when Zombie far from us and less than 2 heals left. here we become aggressive.    
            if  closestzdist>closestzthreshold and self.healcount >3:
                self.scan = 0
                if self.getHealth() < self.getInitHealth() * healththresh*0.8 and self.healcount <5:
                    self.healcount +=1
                    return HealEvent(self)
                else:
                    if len(self.getScanResults())==0:
                        xzdiff = x - int(size_x/2) 
                        yzdiff = y - int(size_y/2)   
                    if len(self.getScanResults())!=0:
                        xzdiff = x - xz # Diff x coordinate of nearest zombie
                        yzdiff = y - yz # Diff y coordinate of nearest zombie
                    if abs(xzdiff) + abs(yzdiff) >3:
                        if abs(xzdiff)>abs(yzdiff):
                            xzdiff = 2*numpy.sign(xzdiff)
                            if yzdiff == 0:                                
                                xzdiff = 3
                            yzdiff = 1*numpy.sign(yzdiff)
                        else:
                            xzdiff = 1*numpy.sign(xzdiff)
                            yzdiff = 2*numpy.sign(yzdiff)
                            if xzdiff == 0:
                                yzdiff = 3
                    if x - xzdiff < 0 or x - xzdiff >= size_x:
                        xzdiff = 0
                    if y - yzdiff < 0 or y - yzdiff >= size_y:
                        yzdiff = 0
                    return MoveEvent(self, x - xzdiff, y - yzdiff)#Moving towards zombie or center
            pass
