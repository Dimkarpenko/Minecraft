from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.panel import Panel
from ursina.shaders import *
from perlin_noise import PerlinNoise
from numpy import floor,abs
from random import randint,randrange
import psutil
import os
import json

version = '0.0.4a'

app = Ursina()

global block_pick
global spawnpoint

application.development_mode = False

with open('launch.json') as json_file:
	data = json.load(json_file)
	render_fog = data["scene"][0]["render_fog"]
	terrainWidth = data["scene"][0]["terrainwidth"]
	enable_shaders = data["scene"][0]["enable_shaders"]
	window.borderless = data["window"][0]["borderless"]
	window.fullscreen = data["window"][0]["fullscreen"]
	window.render_mode = data["window"][0]["render_mode"]
	nickname = data["scene"][0]["nickname"]

grass_texture = load_texture('assets/textures/grass_block.png')
stone_texture = load_texture('assets/textures/stone_block.png')
brick_texture = load_texture('assets/textures/brick_block.png')
dirt_texture  = load_texture('assets/textures/dirt_block.png')
plank_texture = load_texture('assets/textures/planks_block.png')
sand_texture = load_texture('assets/textures/sand_block.png')
gravel_texture = load_texture('assets/textures/gravel_block.png')
oak_texture = load_texture('assets/textures/oak_block.png')
oak_leaf_texture = load_texture('assets/textures/oak_leaf_block.png')
cobblestone_texture = load_texture('assets/textures/cobblestone_block.png')
granite_texture = load_texture('assets/textures/granite_block.png')
bedrock_texture = load_texture('assets/textures/bedrock_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/hand.png')
inventory_texture   = load_texture('assets/inventory_point.png')
cursor_texture = load_texture('assets/crosshair.png')
punch_sound   = Audio('assets/audio/break1',loop = False, autoplay = False)
block_pick = 0
spawnpoint = (0,0,0)

grass_texture_2 = load_texture('assets/textures/grass_texture.png')
stone_texture_2 = load_texture('assets/textures/stone_texture.png')
brick_texture_2 = load_texture('assets/textures/brick_texture.png')
dirt_texture_2 = load_texture('assets/textures/dirt_texture.png')
plank_texture_2 = load_texture('assets/textures/planks_texture.png')
sand_texture_2 = load_texture('assets/textures/sand_texture.png')
gravel_texture_2 = load_texture('assets/textures/gravel_texture.png')
oak_texture_2 = load_texture('assets/textures/oak_texture.png')
oak_leaf_texture_2 = load_texture('assets/textures/oak_leaf_texture.png')
cobblestone_texture_2 = load_texture('assets/textures/cobblestone_texture.png')
granite_texture_2 = load_texture('assets/textures/granite_texture.png')

window.title = f"Minecraft {version}"
window.icon = "assets/icon.ico"
button_font = 'assets/fonts/minecraft.ttf'
window.exit_button.visible = False
window.fps_counter.visible = False
window.center_on_screen()

if render_fog == True:
	scene.fog_color = color.white
	scene.fog_density = 0.02

if enable_shaders == True:
	Entity.default_shader = lit_with_shadows_shader
	sun = DirectionalLight()
	sun.look_at(Vec3(1,-1,-1))

o = Panel(scale=5)
o.visible = False

version = Text(position=Vec3(-.87,0.48,0),font = button_font,text=version)
coordinates = Text(position=Vec3(-.87,0.44,0),font = button_font)
cpu_panel = Text(position=Vec3(-.87,0.40,0),font = button_font,ignore_paused=True)
block_name_l = Text(position=Vec3(-0.05,-.4,0),font = button_font)
console_output = Text(position=Vec3(-.87,-.4,0),font = button_font)

terrain = Entity(model=None,collider=None)
noise = PerlinNoise(octaves=2,seed=int(randrange(100,999)))

amp = 6
freq = 24
fps=60
i=0
cpu = 0
ram = 0
max_y = 0
block_names = {}
block_ids = {}

def check_fall():
	if player.y < -110.0:
		PlayerCommands.kill(message=f'Player {nickname} fell out of the world')

def update():
	global block_pick,fps,i,max_y,cpu,ram,block_names,block_name_l,block_ids
	check_fall()

	if i > 60:
		fps = str(int(1//time.dt))
		cpu = psutil.cpu_percent()
		ram = psutil.virtual_memory().percent
		i = 0
	i += 1

	pid = os.getpid()
	python_process = psutil.Process(pid)
	memoryUse = python_process.memory_info()[0]/2.**30

	coordinates.text = f'Position: {round(player.x)},{round(player.y)},{round(player.z)} / {fps} fps'
	cpu_panel.text = f'CPU: {cpu}% / RAM: {ram}% / Memory use: {round(memoryUse,2)} GB'

	if held_keys['left mouse'] or held_keys['right mouse']:
		hand.active()
	else:
		hand.passive()

	if held_keys['escape']: application.quit()
	if held_keys['e']:
		application.pause()
		o.visible = True
		inventory.visible = True
		mouse.locked = False
		mouse.visible = True
	if held_keys['p']:PlayerCommands.setspawn(player.x,player.y,player.z)
	if held_keys['r']:PlayerCommands.move_random()
	if held_keys['k']:PlayerCommands.kill(message=f'Player {nickname} killed')

class PlayerCommands():
	global spawnpoint
	def __init__(self,**kwargs):
		pass
	
	def kill(message):
		player.position=spawnpoint
		console_output.text = message

	def setspawn(x,y,z):
		global spawnpoint
		spawnpoint = (x,y,z)
		console_output.text = f'Spawnpoint set {round(x)},{round(y)},{round(z)}'

	def move_random():
		rand_x = randint(0,terrainWidth-2)
		rand_z = randint(0,terrainWidth-2)
		player.position = (rand_x,max_y,rand_z)
		console_output.text = f'Player {nickname} moved to {round(rand_x)},{round(max_y)},{round(rand_z)}'

current_block = Button(position=Vec2(.82,0.42),scale=.1,model='quad',color=color.white,disabled=True,texture=grass_texture_2,visible=False)

class Inventory(Entity):
    global block_pick,block_names
    def __init__(self,**kwargs):
        super().__init__(
            parent = camera.ui,
            model = 'quad',
            scale = (.5, .7),
            origin = (-.5, .5),
            position = (-.25,.35),
            texture = inventory_texture,
            texture_scale = (5,7),
            color = color.rgb(198,198,198, a=255)
            )

        self.item_parent = Entity(parent=self, scale=(1/5,1/7))

    def find_free_spot(self):                                                      
        taken_spots = [(int(e.x), int(e.y)) for e in self.item_parent.children]    
        for y in range(7):                                                         
            for x in range(5):                                                     
                if not (x,-y) in taken_spots:                                      
                    return (x,-y)   

    def append(self,item,texture,id):
        inv = Button(
		    parent = inventory.item_parent,
		    model = 'quad',
		    origin = (-.66,.66),
			scale = .75,
		    color = color.white,
			texture = texture,
		    position = self.find_free_spot(),                                       
		    z = -.1,
		    )
        block_names[id] = item
        block_ids[id] = texture

        def choose_block():
            global block_pick
            mouse.locked = True
            mouse.visible = False
            inventory.visible = False
            o.visible = False
            application.resume() 
            block_pick = id
            if block_pick != 0:
                block_name_l.visible = True
                current_block.visible = True
                block_name_l.text = str(block_names[block_pick])
                current_block.texture = block_ids[block_pick]
            if block_pick == 0:
                block_name_l.visible = False
                current_block.visible = False
		
        inv.on_click = choose_block

class Voxel(Button):
	def __init__(self, position = (0,0,0), texture = grass_texture):
		super().__init__(
			parent = scene,
			position = position,
			model = 'assets/block',
			origin_y = 0.5,
			texture = texture,
			color = color.color(0,0,random.uniform(0.9,1)),
			scale = 0.5,
			)

	def input(self,key):
		if self.hovered:
			if key == 'right mouse down' and block_pick != 0:
				punch_sound.play()
				if block_pick == 1: voxel = Voxel(position = self.position + mouse.normal, texture = grass_texture)
				if block_pick == 2: voxel = Voxel(position = self.position + mouse.normal, texture = stone_texture)
				if block_pick == 3: voxel = Voxel(position = self.position + mouse.normal, texture = brick_texture)
				if block_pick == 4: voxel = Voxel(position = self.position + mouse.normal, texture = dirt_texture)
				if block_pick == 5: voxel = Voxel(position = self.position + mouse.normal, texture = plank_texture)
				if block_pick == 6: voxel = Voxel(position = self.position + mouse.normal, texture = sand_texture)
				if block_pick == 7: voxel = Voxel(position = self.position + mouse.normal, texture = gravel_texture)
				if block_pick == 8: voxel = Voxel(position = self.position + mouse.normal, texture = oak_texture)
				if block_pick == 9: voxel = Voxel(position = self.position + mouse.normal, texture = oak_leaf_texture)
				if block_pick == 10: voxel = Voxel(position = self.position + mouse.normal, texture = cobblestone_texture)
				if block_pick == 11: voxel = Voxel(position = self.position + mouse.normal, texture = granite_texture)

			if key == 'left mouse down':
				if self.texture != bedrock_texture:
					punch_sound.play()
					destroy(self)

class Hand(Entity):
	def __init__(self):
		super().__init__(
			parent = camera.ui,
			model = 'assets/arm',
			texture = arm_texture,
			scale = 0.2,
			rotation = Vec3(150,-10,0),
			position = Vec2(0.4,-0.6))

	def active(self):
		self.position = Vec2(0.3,-0.5)

	def passive(self):
		self.position = Vec2(0.4,-0.6)

#render terrain
for i in range(terrainWidth*terrainWidth):
    voxel = Voxel(texture=grass_texture)
    voxel.x = floor(i/terrainWidth)
    voxel.z = floor(i%terrainWidth)
    voxel.y = floor((noise([voxel.x/freq,voxel.z/freq]))*amp)
    if voxel.y > max_y:max_y = voxel.y
'''
for b in range(1):
	for i in range(terrainWidth*terrainWidth):
		voxel = Voxel(texture=dirt_texture)
		voxel.x = floor(i/terrainWidth)
		voxel.z = floor(i%terrainWidth)
		voxel.y = floor(((noise([voxel.x/freq,voxel.z/freq]))*amp)-(b+1))
'''
for b in range(1):
	for i in range(terrainWidth*terrainWidth):
		voxel = Voxel(texture=bedrock_texture)
		voxel.x = floor(i/terrainWidth)
		voxel.z = floor(i%terrainWidth)
		voxel.y = floor(((noise([voxel.x/freq,voxel.z/freq]))*amp)-(b+1))

terrain.combine()
terrain.collider = 'mesh'
terrain.texture = grass_texture

player = FirstPersonController()
spawnpoint = (terrainWidth/2,8,terrainWidth/2)
player.position = spawnpoint
player.cursor.disable()
player.cursor = Entity(parent=camera.ui, model='quad', color=color.white, scale=.03,rotation_z=90,texture=cursor_texture,default_shader=None) 
player.gravity = 0.6
#camera.fov = 150

sky = Sky(texture=sky_texture)
hand = Hand()
inventory = Inventory(default_shader=None)
inventory.visible = False

print(f'=====\nterrain width: {terrainWidth}\nseed: {noise.seed}\nplayer spawn: {spawnpoint}\nmax y: {max_y}\nnickname: {nickname}\n=====')
                          
inventory.append('Grass',grass_texture_2,1)
inventory.append('Stone',stone_texture_2,2)
inventory.append('Brick',brick_texture_2,3)  
inventory.append('Dirt',dirt_texture_2,4) 
inventory.append('Planks',plank_texture_2,5) 
inventory.append('Sand',sand_texture_2,6) 
inventory.append('Gravel',gravel_texture_2,7) 
inventory.append('Oak',oak_texture_2,8) 
inventory.append('Leaf',oak_leaf_texture_2,9) 
inventory.append('Cobblestone',cobblestone_texture_2,10) 
inventory.append('Granite',granite_texture_2,11) 

app.run()
