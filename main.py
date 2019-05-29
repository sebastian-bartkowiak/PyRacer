import arcade
import math

SCREEN_TITLE = "Starting Template"
DEAD_ZONE = 0.05
ORG_TILE_SIZE = 282
TILE_SCALE = 0.5

DEBUG = True

def deg2rad(deg):
    return (deg*math.pi/180)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class Car(arcade.Sprite):
    def __init__(self,pos_x,pos_y,heading,sprite,scale):
        super().__init__(sprite, scale)
        self.center_x = pos_x
        self.center_y = pos_y
        self.texture = arcade.load_texture(sprite)
        self.scale = scale*0.1
        self.draw_width = self.scale * self.texture.width
        self.draw_height = self.scale * self.texture.height
        self.heading = heading
        self.speed = 0
        self.max_speed = 15
        self.acceleration = 2.5
        self.braking = 3
        self.driving_friction = 0.02
        self.turn_ratio = 2
        self.score = 0
    
    def draw(self):
        arcade.draw_texture_rectangle(self.center_x, self.center_y, self.draw_width, self.draw_height, self.texture, self.heading)
        if DEBUG:
            arcade.draw_rectangle_filled(self.center_x + 75, self.center_y + 125, 100, 200, arcade.color.BLUSH)
            arcade.draw_text("speed: " + str(self.speed), self.center_x + 35, self.center_y + 35, arcade.color.BLACK, 10)
            arcade.draw_text("x:     " + str(self.center_x), self.center_x + 35, self.center_y + 50, arcade.color.BLACK, 10)
            arcade.draw_text("y:     " + str(self.center_y), self.center_x + 35, self.center_y + 65, arcade.color.BLACK, 10)
            arcade.draw_text("h:     " + str(self.heading), self.center_x + 35, self.center_y + 80, arcade.color.BLACK, 10)
            arcade.draw_text("score: " + str(self.score), self.center_x + 35, self.center_y + 95, arcade.color.BLACK, 10)

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

        self.center_x -= math.sin(deg2rad(self.heading))*self.speed
        self.center_y += math.cos(deg2rad(self.heading))*self.speed

        #check collision
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
            temp_line = []
            for j, tile in enumerate(track_line):
                if isValidTrackTile(tile):
                    track_sprite = arcade.Sprite("sprites/track-texture/" + tile + ".png", GRAPHICS_SCALE)
                    track_sprite.top = (i+1)*TILE_SIZE
                    track_sprite.left = j*TILE_SIZE
                    self.track_sprites.append(track_sprite)
            self.window_width = len(track_line) * TILE_SIZE
        self.window_height = len(temp_track_data) * TILE_SIZE

        super().__init__(self.window_width, self.window_height, title)
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.AMAZON)
        self.car = Car(int(start_pos[1])*TILE_SIZE-(TILE_SIZE/2),(len(temp_track_data)-int(start_pos[0]))*TILE_SIZE-(TILE_SIZE/2),int(start_pos[2]),"sprites/car.png",GRAPHICS_SCALE)

        joysticks = arcade.get_joysticks()
        if joysticks:
            self.joystick = joysticks[0]
            self.joystick.open()
        else:
            print("There are no joysticks.")
            self.joystick = None

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