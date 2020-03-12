# Collection of functions to work with a Grid. Stores all its children in the grid array
extends TileMap

enum {EMPTY, TANK}

var x_size = 12
var y_size = 9

var tile_size = get_cell_size()
var half_tile_size = tile_size / 2
var grid_size = Vector2(x_size, y_size)

var grid = []

func _ready():
	for x in range(grid_size.x):
		grid.append([])
		for y in range(grid_size.y):
			grid[x].append(EMPTY)