extends Node2D

# Declare member variables here. Examples:
# var a = 2
# var b = "text"

var tankname = "Tank"
var dead = false

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func init(name, tick0):
	self.tankname = name
	self.position = Vector2(32 + tick0["pos"]["x"] * 64, 32 + tick0["pos"]["y"] * 64)
	$Label.text = self.tankname.split(" - ")[0]
	set_orientation(tick0["facing"])

func set_orientation(facing):
	var dir = facing["__enum__"]
	if dir == "Direction.SOUTH":
		self.get_node("Sprite").rotation_degrees = 0.0
	elif dir == "Direction.NORTH":
		self.get_node("Sprite").rotation_degrees = 180.0
	elif dir == "Direction.EAST":
		self.get_node("Sprite").rotation_degrees = 270.0
	elif dir == "Direction.WEST":
		self.get_node("Sprite").rotation_degrees = 90.0
	
func run_tick(tick):
	var x = tick["pos"]["x"]
	var y = tick["pos"]["y"]
	self.position = Vector2(32 + x * 64, 32 + y * 64)
	
	set_orientation(tick["facing"])
	if tick["hp"] <= 0:
		self.dead = true
		self.visible = false
	else:
		self.visible = true
		if "hit" in tick and tick["hit"]:
			self.get_node("Sprite").modulate = Color(1,0.25,0.25)
		else:
			self.get_node("Sprite").modulate = Color(1,1,1)
	

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
