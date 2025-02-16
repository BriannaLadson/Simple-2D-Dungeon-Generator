from tkinter import *
import random

class Root(Tk):
	def __init__(self):
		super().__init__()
		self.title("Simple Dungeon Generation")
		self.state("zoomed")
		
		self.dungeon_canvas = DungeonCanvas(self)
		self.dungeon_canvas.pack(fill=BOTH, expand=1)
		self.dungeon_canvas.update()
		
		self.dungeon_canvas.generate_dungeon_level()
		
		self.bind("<Up>", lambda e: self.dungeon_canvas.move_player(0, -1))
		self.bind("<Down>", lambda e: self.dungeon_canvas.move_player(0, 1))
		self.bind("<Left>", lambda e: self.dungeon_canvas.move_player(-1, 0))
		self.bind("<Right>", lambda e: self.dungeon_canvas.move_player(1, 0))
		
		self.bind("<Shift-Up>", lambda e: self.dungeon_canvas.move_player_up())
		self.bind("<Shift-Down>", lambda e: self.dungeon_canvas.move_player_down())
		
class Player:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0
		
class DungeonCanvas(Canvas):
	def __init__(self, parent):
		super().__init__(parent, bg="black")
		
		self.player = Player()
		
		self.tile_colors = {
			0: "#fed6d3", #Floor/No Wall
			1: "gray", #Wall
			2: "blue", #Upstairs
			3: "green", #Downstairs
		}
		
		self.dungeon_level_size = 25
		self.dungeon_map = []
		
		self.min_room_size = 3
		self.max_room_size = 6
		
		self.max_rooms = 10
		
		self.max_failure = 10
		
		self.staircases = []
		
	def generate_dungeon_level(self):
		self.fill_level_with_walls()
		
		self.place_rooms()
		
		self.connect_rooms()
		
		self.place_stairs()
		
		self.place_player()
		
		self.draw_dungeon_level()
		
		self.draw_player()
		
	def fill_level_with_walls(self):
		z_array = []
		
		for y in range(self.dungeon_level_size):
			y_array = []
			
			for x in range(self.dungeon_level_size):
				y_array.append(1)
				
			z_array.append(y_array)
			
		self.dungeon_map.append(z_array)
		
	def place_rooms(self):
		z_array = self.dungeon_map[-1]
		self.rooms = []
		
		room_num = 0
		failure_num = 0
		
		while room_num < self.max_rooms or failure_num <= self.max_failure:
			#Room Center
			room_x = random.randint(0, self.dungeon_level_size - 1)
			room_y = random.randint(0, self.dungeon_level_size - 1)
			
			#Room Width/Height
			room_w = random.randint(self.min_room_size, self.max_room_size)
			room_h = random.randint(self.min_room_size, self.max_room_size)
			
			#Room Bounds
			x1 = room_x - room_w // 2
			y1 = room_y - room_h // 2
			
			x2 = room_x + room_w // 2
			y2 = room_y + room_h // 2
			
			#Is Room Within Map Bounds?
			if x1 < 0 or y1 < 0 or x2 >=self.dungeon_level_size or y2 >= self.dungeon_level_size:
				failure_num += 1
				continue
				
			#Does Room Overlap w/ Other Rooms?
			if self.does_overlap(x1, y1, x2, y2):
				failure_num += 1
				continue
				
			#Place Room
			for y in range(y1, y2 + 1):
				for x in range(x1, x2 + 1):
					z_array[y][x] = 0
					
			self.rooms.append((x1,y1,x2,y2))
			room_num += 1
				
	def does_overlap(self, x1, y1, x2, y2):
		for room in self.rooms:
			rx1, ry1, rx2, ry2 = room
			
			if not (x2 < rx1 or x1 > rx2 or y2 < ry1 or y1 > ry2):
				return True
				
		return False
		
	def connect_rooms(self):
		for i in range(len(self.rooms) - 1):
			room1 = self.rooms[i]
			room2 = self.rooms[i + 1]
			
			x1, y1 = (room1[0] + room1[2]) // 2, (room1[1] + room1[3]) // 2
			x2, y2 = (room2[0] + room2[2]) // 2, (room2[1] + room2[3]) // 2
			
			self.create_corridor(x1, y1, x2, y2)
			
	def create_corridor(self, x1, y1, x2, y2):
		if random.choice([True, False]):
			for x in range(min(x1, x2), max(x1, x2) + 1):
				self.dungeon_map[-1][y1][x] = 0
				
			for y in range(min(y1, y2), max(y1, y2) + 1):
				self.dungeon_map[-1][y][x2] = 0
				
		else:
			for y in range(min(y1, y2), max(y1, y2) + 1):
				self.dungeon_map[-1][y][x1] = 0
				
			for x in range(min(x1, x2), max(x1, x2) + 1):
				self.dungeon_map[-1][y2][x] = 0
				
	def place_stairs(self):
		z_array = self.dungeon_map[-1]
		
		idx = self.dungeon_map.index(z_array)
		
		while True:
			x = random.randint(0, self.dungeon_level_size - 1)
			y = random.randint(0, self.dungeon_level_size - 1)
			
			tile = self.dungeon_map[idx][y][x]
			
			if tile == 0:
				self.dungeon_map[idx][y][x] = 2
				
				self.up_stairs = (x,y)
				
				break
				
		while True:
			x = random.randint(0, self.dungeon_level_size - 1)
			y = random.randint(0, self.dungeon_level_size - 1)
			
			tile = self.dungeon_map[idx][y][x]
			
			if tile == 0:
				self.dungeon_map[idx][y][x] = 3
				
				self.down_stairs = (x, y)
				
				break
				
		self.staircases.append({
			"up": self.up_stairs,
			"down": self.down_stairs,
		})

	def place_player(self):
		z_array = self.dungeon_map[self.player.z]
		idx = self.dungeon_map.index(z_array)
		
		if idx == 0:
			self.player.x, self.player.y = self.up_stairs
			
	def draw_player(self):
		self.delete("player")
		
		tile_w = self.winfo_width() / self.dungeon_level_size
		tile_h = self.winfo_height() / self.dungeon_level_size
		
		scale = .5
		
		diameter = min(tile_w, tile_h) * scale
		
		x = self.player.x * tile_w + (tile_w - diameter) / 2
		y = self.player.y * tile_h + (tile_h - diameter) / 2
		
		x1 = x + diameter
		y1 = y + diameter
		
		self.create_oval(
			x,
			y,
			x1,
			y1,
			fill="red",
			width=2,
			tags=("player"),
		)
		
	def draw_dungeon_level(self):
		self.delete("all")
		
		z_array = self.dungeon_map[self.player.z]
		
		tile_w = self.winfo_width() / self.dungeon_level_size
		tile_h = self.winfo_height() / self.dungeon_level_size
		
		for y in range(self.dungeon_level_size):
			for x in range(self.dungeon_level_size):
				tile = z_array[y][x]
				
				tile_color = self.tile_colors[tile]
				
				tile_x = x * tile_w
				tile_y = y * tile_h
				
				tile_x1 = tile_x + tile_w
				tile_y1 = tile_y + tile_h
				
				self.create_rectangle(
					tile_x,
					tile_y,
					tile_x1,
					tile_y1,
					fill=tile_color,
				)
				
	def move_player(self, dx, dy):
		new_x = self.player.x + dx
		new_y = self.player.y + dy
		
		if 0 <= new_x < self.dungeon_level_size and 0 <= new_y < self.dungeon_level_size:
			if self.dungeon_map[self.player.z][new_y][new_x] != 1:
				self.player.x = new_x
				self.player.y = new_y
				
				self.draw_player()
				
	def move_player_up(self):
		if self.dungeon_map[self.player.z][self.player.y][self.player.x] == 2:
			if self.player.z == 0:
				self.master.destroy()
				
			else:
				self.player.z -= 1
				
				self.player.x, self.player.y = self.staircases[self.player.z]["down"]
				
				self.draw_dungeon_level()
				self.draw_player()
				
	def move_player_down(self):
		if self.dungeon_map[self.player.z][self.player.y][self.player.x] == 3:
			self.player.z += 1
			
			if self.player.z > len(self.dungeon_map) - 1:
				self.generate_dungeon_level()
				
			self.player.x, self.player.y = self.staircases[self.player.z]["up"]
			
			self.draw_dungeon_level()
			self.draw_player()
		
if __name__ == "__main__":
	root = Root()
	root.mainloop()