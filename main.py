import arcade
import math
import sys

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
        self.speed = 10
        self.max_speed = 15
        self.acceleration = 2.5
        self.braking = 3
        #self.driving_friction = 0.02
        self.driving_friction = 0
        self.steering_friction = 0.1
        self.turn_ratio = 2
        self.wheels_turn = 30
        self.wheels_snap = 0.25
        self.max_wheels_turn = 30
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

    def draw(self):
        if DEBUG:
            arcade.draw_rectangle_filled(60, 67.5, 100, 115, arcade.color.BLUSH)
            arcade.draw_text("speed: " + str(round(self.speed,3)), 25, 100, arcade.color.BLACK, 10)
            arcade.draw_text("x:     " + str(round(self.center.x,3)), 25, 85, arcade.color.BLACK, 10)
            arcade.draw_text("y:     " + str(round(self.center.y,3)), 25, 70, arcade.color.BLACK, 10)
            arcade.draw_text("h:     " + str(round(self.heading,3)), 25, 55, arcade.color.BLACK, 10)
            arcade.draw_text("wh:    " + str(round(self.wheels_turn,3)), 25, 40, arcade.color.BLACK, 10)
            arcade.draw_text("score: " + str(round(self.score,3)), 25, 25, arcade.color.BLACK, 10)

            if self.turn_center is not None:
                self.turn_center.draw(arcade.color.GREEN)
            if self.turn_radius is not None:
                arcade.draw_circle_outline(self.turn_center.x,self.turn_center.y,self.turn_radius,arcade.color.GREEN,2)
            self.front_wheel.draw(arcade.color.RED)
            self.center.draw(arcade.color.YELLOW)
            self.rear_wheel.draw(arcade.color.BLUE)
            arcade.draw_rectangle_outline(self.center.x,self.center.y,self.width,self.length,arcade.color.BLACK,2,self.heading)
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
            self.wheels_turn -= self.steering_friction
        elif self.wheels_turn < 0:
            self.wheels_turn += self.steering_friction
        if self.wheels_turn < self.wheels_snap and self.wheels_turn > (-1)*self.wheels_snap:
            self.wheels_turn = 0
        if ((steer_dir > DEAD_ZONE) or steer_dir < (-1*DEAD_ZONE)):
            self.wheels_turn -= steer_dir*self.turn_ratio
        if self.wheels_turn > self.max_wheels_turn:
            self.wheels_turn = self.max_wheels_turn
        elif self.wheels_turn < (-1)*self.max_wheels_turn:
            self.wheels_turn = (-1)*self.max_wheels_turn

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
        #TODO - check collision
        self.score += self.speed

def isValidTrackTile(tile):
    return tile == "SRL" or tile == "STD" or tile == "TDL" or tile == "TRD" or tile == "TUL" or tile == "TUR"

class MyGame(arcade.Window):

    def __init__(self, title, track_file):
        temp_track_data = []
        start_pos = ''
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
                    track_sprite = arcade.Sprite("sprites/track-texture/" + tile + ".png", GRAPHICS_SCALE)
                    track_sprite.top = (i+1)*TILE_SIZE
                    track_sprite.left = j*TILE_SIZE
                    self.track_sprites.append(track_sprite)
            self.window_width = len(track_line) * TILE_SIZE
        self.window_height = len(temp_track_data) * TILE_SIZE

        super().__init__(self.window_width, self.window_height, title)
        #self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.AMAZON)
        self.car = Car(int(start_pos[1])*TILE_SIZE-(TILE_SIZE/2),(len(temp_track_data)-int(start_pos[0]))*TILE_SIZE-(TILE_SIZE/2),int(start_pos[2]),"sprites/car.png",GRAPHICS_SCALE)

        joysticks = arcade.get_joysticks()
        if joysticks:
            self.joystick = joysticks[0]
            self.joystick.open()
        else:
            print("No joysticks found! Exiting...")
            sys.exit(1)

    def on_draw(self):
        arcade.start_render()
        self.track_sprites.draw()
        self.car.draw()

    def update(self, delta_time):
        self.car.update(self.joystick.x,self.joystick.z*(-1))

def main():
    game = MyGame("PyRacer", "test.csv")
    arcade.run()

if __name__ == "__main__":
    main()