import arcade
import math
import sys
import datetime

SCREEN_TITLE = "Starting Template"
DEAD_ZONE = 0.05
ORG_TILE_SIZE = 282
TILE_SCALE = 0.5

DEBUG = True

class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def draw(self, color):
        arcade.draw_point(self.x, self.y, color, 10)

class Line:
    def __init__(self,centerPoint,length,angle):
        self.center = centerPoint
        self.length = length
        self.angle = angle

    def draw(self, color):
        arcade.draw_line(self.center.x - math.sin(math.radians(self.angle))*(self.length/2), self.center.y + math.cos(math.radians(self.angle))*(self.length/2),self.center.x + math.sin(math.radians(self.angle))*(self.length/2), self.center.y - math.cos(math.radians(self.angle))*(self.length/2),color, 2)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class Car:
    def __init__(self,pos_x,pos_y,heading,sprite,scale):
        self.center = Point(pos_x,pos_y)
        self.heading = heading
        self.speed = 5
        self.max_speed = 15
        self.acceleration = 2.5
        self.braking = 3
        self.driving_friction = 0.03
        self.steering_friction = 0.01
        self.turn_ratio = 2
        self.wheels_turn = -5
        self.wheels_snap = 0.25
        
        self.score = 0
        self.length = 920*0.1*scale
        self.width = 480*0.1*scale

        self.sprite = arcade.Sprite(sprite,scale*0.1)
        self.sprite.center_x = self.center.x
        self.sprite.center_y = self.center.y
        self.sprite.angle = self.heading

        if DEBUG:
            self.front_wheel = Line(Point(self.center.x - math.sin(math.radians(self.heading))*(self.length/2), self.center.y + math.cos(math.radians(self.heading))*(self.length/2)),20,self.heading + self.wheels_turn)
        self.rear_wheel = Line(Point(self.center.x + math.sin(math.radians(self.heading))*(self.length/2), self.center.y - math.cos(math.radians(self.heading))*(self.length/2)),20,self.heading)
        self.turn_center = None
        self.turn_radius = None
    
    #limits wheels turn for higher travel speed
    def getMaxWheelsTurn(self):
        return map(self.speed,0,self.max_speed,45,15)

    #draw function
    def draw(self):
        if DEBUG:
            arcade.draw_rectangle_filled(60, 67.5, 100, 130, arcade.color.BLUSH)
            arcade.draw_text("speed: " + str(round(self.speed,3)), 25, 115, arcade.color.BLACK, 10)
            arcade.draw_text("x:     " + str(round(self.center.x,3)), 25, 100, arcade.color.BLACK, 10)
            arcade.draw_text("y:     " + str(round(self.center.y,3)), 25, 85, arcade.color.BLACK, 10)
            arcade.draw_text("h:     " + str(round(self.heading,3)), 25, 70, arcade.color.BLACK, 10)
            arcade.draw_text("wh:    " + str(round(self.wheels_turn,3)), 25, 55, arcade.color.BLACK, 10)
            arcade.draw_text("Mwh:   " + str(round(self.getMaxWheelsTurn(),3)), 25, 40, arcade.color.BLACK, 10)
            arcade.draw_text("score: " + str(round(self.score,3)), 25, 25, arcade.color.BLACK, 10)

            if self.turn_center is not None:
                self.turn_center.draw(arcade.color.GREEN)
            if self.turn_radius is not None:
                arcade.draw_circle_outline(self.turn_center.x,self.turn_center.y,self.turn_radius,arcade.color.GREEN,2)
            self.front_wheel.draw(arcade.color.RED)
            self.center.draw(arcade.color.YELLOW)
            self.rear_wheel.draw(arcade.color.BLUE)
            arcade.draw_rectangle_outline(self.center.x,self.center.y,self.width,self.length,arcade.color.YELLOW,2,self.heading)
        else:
            self.sprite.draw()

    def update(self,steer_dir,steer_vel):
        self.speed -= self.driving_friction
        if steer_vel > DEAD_ZONE:
            self.speed += steer_vel*self.acceleration
        elif steer_vel < (-1*DEAD_ZONE):
            self.speed += steer_vel*self.braking
        
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        elif self.speed < 0:
            self.speed = 0

        if self.wheels_turn > 0:
            self.wheels_turn -= self.steering_friction*self.speed
        elif self.wheels_turn < 0:
            self.wheels_turn += self.steering_friction*self.speed
        if self.wheels_turn < self.wheels_snap and self.wheels_turn > (-1)*self.wheels_snap:
            self.wheels_turn = 0
        if ((steer_dir > DEAD_ZONE) or steer_dir < (-1*DEAD_ZONE)):
            self.wheels_turn -= steer_dir*self.turn_ratio
        if self.wheels_turn > self.getMaxWheelsTurn():
            self.wheels_turn = self.getMaxWheelsTurn()
        elif self.wheels_turn < (-1)*self.getMaxWheelsTurn():
            self.wheels_turn = (-1)*self.getMaxWheelsTurn()

        if self.wheels_turn != 0:
            self.turn_radius = self.length/math.tan(math.radians(self.wheels_turn))
            self.turn_center = Point(self.rear_wheel.center.x - math.sin(math.radians(self.heading + 90))*self.turn_radius,self.rear_wheel.center.y + math.cos(math.radians(self.heading + 90))*self.turn_radius)
            circle_angle = (180*self.speed)/(math.pi*self.turn_radius)
            stop_angle = self.heading + math.copysign(90,self.turn_radius) + 180 + circle_angle
            new_rear_wheel = Point(self.turn_center.x - math.copysign(self.turn_radius,1) * math.sin(math.radians(stop_angle)),self.turn_center.y + math.copysign(self.turn_radius,1) * math.cos(math.radians(stop_angle)))
            self.heading += circle_angle
            self.center.x = new_rear_wheel.x - (self.length/2) * math.sin(math.radians(self.heading))
            self.center.y = new_rear_wheel.y + (self.length/2) * math.cos(math.radians(self.heading))
        else:
            self.turn_center = None
            self.turn_radius = None
            self.center.x -= math.sin(math.radians(self.heading))*self.speed
            self.center.y += math.cos(math.radians(self.heading))*self.speed
        
        if DEBUG:
            self.front_wheel.center = Point(self.center.x - math.sin(math.radians(self.heading))*(self.length/2), self.center.y + math.cos(math.radians(self.heading))*(self.length/2))
            self.front_wheel.angle = self.heading + self.wheels_turn
        self.rear_wheel.center =  Point(self.center.x + math.sin(math.radians(self.heading))*(self.length/2), self.center.y - math.cos(math.radians(self.heading))*(self.length/2))
        self.rear_wheel.angle = self.heading
        
        self.sprite.center_x = self.center.x
        self.sprite.center_y = self.center.y
        self.sprite.angle = self.heading
        self.score += self.speed

def isValidTrackTile(tile):
    return tile == "SRL" or tile == "STD" or tile == "TDL" or tile == "TRD" or tile == "TUL" or tile == "TUR"

class MyGame(arcade.Window):
    def __init__(self, title, track_file):
        temp_track_data = []
        start_pos = ''
        track_sprite_dir = "sprites/track-structure/"
        track_sprite_ext = ".bmp"
        with open(track_file) as track_data:
            GRAPHICS_SCALE = float(track_data.readline())
            TILE_SIZE = int(ORG_TILE_SIZE * GRAPHICS_SCALE)
            start_pos = track_data.readline().split(',')
            temp_track_data = track_data.readlines()
        self.track_sprites = arcade.SpriteList()
        for i, track_line in enumerate(reversed(temp_track_data)):
            track_line = track_line.split(',')
            for j, tile in enumerate(track_line):
                if isValidTrackTile(tile):
                    track_sprite = arcade.Sprite(track_sprite_dir + tile + track_sprite_ext, GRAPHICS_SCALE)
                    track_sprite.top = (i+1)*TILE_SIZE
                    track_sprite.left = j*TILE_SIZE
                    self.track_sprites.append(track_sprite)
            self.window_width = len(track_line) * TILE_SIZE
        self.window_height = len(temp_track_data) * TILE_SIZE

        super().__init__(self.window_width, self.window_height, title)
        self.track_sprites.draw()
        self.track_shape = arcade.get_image()
        if not DEBUG:
            track_sprite_dir = "sprites/track-texture/"
            track_sprite_ext = ".png"
            self.track_sprites = arcade.SpriteList()
            for i, track_line in enumerate(reversed(temp_track_data)):
                track_line = track_line.split(',')
                for j, tile in enumerate(track_line):
                    if isValidTrackTile(tile):
                        track_sprite = arcade.Sprite(track_sprite_dir + tile + track_sprite_ext, GRAPHICS_SCALE)
                        track_sprite.top = (i+1)*TILE_SIZE
                        track_sprite.left = j*TILE_SIZE
                        self.track_sprites.append(track_sprite)
            arcade.set_background_color(arcade.color.AMAZON)
        else:
            self.distance_lines = []
            arcade.set_background_color(arcade.color.WHITE)

        self.car = Car(int(start_pos[1])*TILE_SIZE-(TILE_SIZE/2),(len(temp_track_data)-int(start_pos[0]))*TILE_SIZE-(TILE_SIZE/2),int(start_pos[2]),"sprites/car.png",GRAPHICS_SCALE)
        self.distance_angles = [-90,-60,-30,0,30,60,90]
        self.end = False
        self.steer_dir = 0
        self.steer_speed = 0
        self.data_file = open("NN_data/" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") + ".txt","w")

        joysticks = arcade.get_joysticks()
        if joysticks:
            self.joystick = joysticks[0]
            self.joystick.open()
        """ else:
            print("No joysticks found! Exiting...")
            sys.exit(1) """

    def checkPixelIsCollision(self,point):
        return self.track_shape.getpixel((int(point.x),int(self.window_height-point.y)))[3] == 0

    def on_draw(self):
        arcade.start_render()
        self.track_sprites.draw()
        if DEBUG and len(self.distance_lines):
            arcade.draw_lines(self.distance_lines, arcade.color.BLUE, 3)
            self.front_left_car_corner.draw(arcade.color.WHITE)
            self.front_right_car_corner.draw(arcade.color.GREEN)
        self.car.draw()

    def update(self, delta_time):
        if not self.end:
            data_line = []
            """ 
                data_line structure:
                - first N values are distances to wall in each of directions specified in self.distance_angles
                - car speed before steering update
                - car wheels turn angle before steering update
                - direction steering value from previous time slot
                - speed steering value from previous time slot
                - direction steering value from current time slot
                - speed steering value from current time slot
            """
            if DEBUG:
                self.distance_lines = []
                #self.distance_lines.append((300,200))
            #calculate distances
            for angle in self.distance_angles:
                heading_corrected_angle = self.car.heading - angle
                distance_to_hit = 0
                check_point = Point(self.car.center.x - math.sin(math.radians(heading_corrected_angle))*distance_to_hit, self.car.center.y + math.cos(math.radians(heading_corrected_angle))*distance_to_hit)
                while not self.checkPixelIsCollision(check_point):
                    distance_to_hit += 0.25
                    check_point = Point(self.car.center.x - math.sin(math.radians(heading_corrected_angle))*distance_to_hit, self.car.center.y + math.cos(math.radians(heading_corrected_angle))*distance_to_hit)
                data_line.append(distance_to_hit)
                if DEBUG:
                    self.distance_lines.append((self.car.center.x,self.car.center.y))
                    self.distance_lines.append((check_point.x,check_point.y))
            data_line.append(self.car.speed)
            data_line.append(self.car.wheels_turn)
            data_line.append(self.steer_dir)
            data_line.append(self.steer_speed)
            #self.steer_dir = self.joystick.x
            #self.steer_speed = self.joystick.z*(-1)
            self.steer_dir = 0.1
            self.steer_speed = 0.2
            data_line.append(self.steer_dir)
            data_line.append(self.steer_speed)
            for entry in data_line:
                self.data_file.write(str(entry) + ",")
            self.data_file.write("\n")
            self.car.update(self.steer_dir,self.steer_speed)
            #check for collision
            self.front_left_car_corner  = Point(self.car.center.x - math.sin(math.radians(self.car.heading))*(self.car.length/2), self.car.center.y + math.cos(math.radians(self.car.heading))*(self.car.length/2))
            self.front_left_car_corner.x -=  math.sin(math.radians(self.car.heading + 90))*(self.car.width/2)
            self.front_left_car_corner.y +=  math.cos(math.radians(self.car.heading + 90))*(self.car.width/2)
            self.front_right_car_corner = Point(self.car.center.x - math.sin(math.radians(self.car.heading))*(self.car.length/2), self.car.center.y + math.cos(math.radians(self.car.heading))*(self.car.length/2))
            self.front_right_car_corner.x -= math.sin(math.radians(self.car.heading - 90))*(self.car.width/2)
            self.front_right_car_corner.y += math.cos(math.radians(self.car.heading - 90))*(self.car.width/2)
            if self.checkPixelIsCollision(self.front_left_car_corner) or self.checkPixelIsCollision(self.front_right_car_corner):
                print('CRASH!')
                self.end = True
                self.car.speed = 0
                self.car.acceleration = 0
                self.data_file.close()

def main():
    game = MyGame("PyRacer", "loop.csv")
    arcade.run()

if __name__ == "__main__":
    main()