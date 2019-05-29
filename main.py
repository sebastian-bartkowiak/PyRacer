import arcade
import math
import sys

SCREEN_TITLE = "Starting Template"
DEAD_ZONE = 0.05
ORG_TILE_SIZE = 282
TILE_SCALE = 0.5

DEBUG = True

def deg2rad(deg):
    return (deg*math.pi/180)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class Car:
    def __init__(self,pos_x,pos_y,heading,sprite,scale):
        self.pos_x = pos_x
        self.pos_y = pos_y
        #self.scale = scale*0.1
        #self.draw_width = self.scale * self.texture.width
        #self.draw_height = self.scale * self.texture.height
        self.heading = heading
        self.speed = 4
        self.max_speed = 15
        self.acceleration = 2.5
        self.braking = 3
        self.driving_friction = 0.02
        self.turn_ratio = 2
        self.score = 0

        self.sprite = arcade.Sprite(sprite,scale*0.1)
        self.sprite.center_x = self.pos_x
        self.sprite.center_y = self.pos_y
        self.sprite.angle = self.heading
    
    def draw(self):
        self.sprite.draw()
        if DEBUG:
            arcade.draw_rectangle_filled(self.pos_x + 75, self.pos_y + 125, 100, 200, arcade.color.BLUSH)
            arcade.draw_text("speed: " + str(round(self.speed,3)), self.pos_x + 35, self.pos_y + 35, arcade.color.BLACK, 10)
            arcade.draw_text("x:     " + str(round(self.pos_x,3)), self.pos_x + 35, self.pos_y + 50, arcade.color.BLACK, 10)
            arcade.draw_text("y:     " + str(round(self.pos_y,3)), self.pos_x + 35, self.pos_y + 65, arcade.color.BLACK, 10)
            arcade.draw_text("h:     " + str(round(self.heading,3)), self.pos_x + 35, self.pos_y + 80, arcade.color.BLACK, 10)
            arcade.draw_text("score: " + str(round(self.score,3)), self.pos_x + 35, self.pos_y + 95, arcade.color.BLACK, 10)

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

        if ((steer_dir > DEAD_ZONE) or steer_dir < (-1*DEAD_ZONE)) and self.speed > 0:
            self.heading -= steer_dir*self.turn_ratio

        self.pos_x -= math.sin(deg2rad(self.heading))*self.speed
        self.pos_y += math.cos(deg2rad(self.heading))*self.speed
        
        self.sprite.center_x = self.pos_x
        self.sprite.center_y = self.pos_y
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
        """ else:
            print("There are no joysticks.")
            sys.exit(1) """

    def on_draw(self):
        arcade.start_render()
        self.track_sprites.draw()
        self.car.draw()

    def update(self, delta_time):
        self.car.update(0,0)
        #self.car.update(self.joystick.x,self.joystick.z*(-1))

def main():
    game = MyGame("PyRacer", "test.csv")
    arcade.run()

if __name__ == "__main__":
    main()