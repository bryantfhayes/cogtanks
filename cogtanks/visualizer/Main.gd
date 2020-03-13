extends Node

const TANK = preload("res://scenes/Tank.tscn")

var _timer = null
var _running = false
var _current_tick = -1
var _playback_speed = 0.35

var gamedata = {}
var ticks = []
var tanks = []

# Called when the node enters the scene tree for the first time.
func _ready():
	set_process(true)
	_timer = Timer.new()
	add_child(_timer)
	
func _process(delta):
	if Input.is_action_pressed("ui_cancel"):
		_running = false
		enableTickButtons(true)
		_timer.stop()
	elif Input.is_action_just_pressed("forward_ten"):
		if _running == false:
			advance_tick(10)
	elif Input.is_action_just_pressed("backwards_ten"):
		if _running == false:
			advance_tick(-10)
	elif Input.is_action_just_pressed("ui_up"):
		change_playback_speed(_playback_speed * 0.75)
	elif Input.is_action_just_pressed("ui_down"):
		change_playback_speed(_playback_speed * 1.5)
	elif Input.is_action_just_pressed("ui_right"):
		if _running == false:
			advance_tick(1)
	elif Input.is_action_just_pressed("ui_left"):
		if _running == false:
			advance_tick(-1)
	
func change_playback_speed(speed):
	_playback_speed = speed
	_timer.set_wait_time(_playback_speed)

func display_tick(curtick):
	$tick_label.text = str(curtick+1)
	
	var jstr = JSON.print(ticks[curtick], " ")
	$text_edit.text = jstr
	
	for tank in tanks:
		if tank.tankname in ticks[curtick]["tanks"]:
			tank.run_tick(ticks[curtick]["tanks"][tank.tankname])
		else:
			tank.visible = false

func enableTickButtons(enabled: bool):
	$run_all_button.disabled = !enabled
	$next_tick_button.disabled = !enabled
	$last_tick_button.disabled = !enabled

func advance_tick(amount):
	_current_tick += amount
	
	if _current_tick < 0:
		_current_tick = 0
		
	if _current_tick >= self.gamedata["gameinfo"]["total_ticks"]:
		_current_tick = self.gamedata["gameinfo"]["total_ticks"] - 1
	
	display_tick(_current_tick)
	
	if _running == true and _current_tick >= self.gamedata["gameinfo"]["total_ticks"] - 1:
		_running = false
		enableTickButtons(true)
		_timer.stop()
		return

func advance_tick_once():
	advance_tick(1)

func runall_ticks():
	if _running == false:
		_running = true
		_current_tick = -1
		enableTickButtons(false)
		_timer.connect("timeout", self, "advance_tick_once")
		_timer.set_wait_time(_playback_speed)
		_timer.set_one_shot(false) # Make sure it loops
		_timer.start()

func loadgame():
	# Load item list with game information
	var gameinfo = gamedata["gameinfo"]
	var starting_tanks = gameinfo["starting_tanks"]
	
	# Clear old children
	tanks = []
	_current_tick = 0
	$tick_label.text = str(_current_tick+1)
	for child in get_node("tank_area_bg/Grid").get_children():
		if "Tank" in child.get_name():
			child.queue_free()
	
	for tank in starting_tanks:
		var new_tank = TANK.instance()
		new_tank.init(tank, ticks[0]["tanks"][tank])
		$tank_area_bg/Grid.add_child(new_tank)
		tanks.append(new_tank)
		
	display_tick(_current_tick)

func _on_load_button_pressed():
	var file = File.new()
	file.open($filepath_entry.text, file.READ)
	var text = file.get_as_text()
	file.close()
	
	var result_json = JSON.parse(text)
	if result_json.error == OK:  # If parse OK
		gamedata = result_json.result
		if "gameinfo" in gamedata and "ticks" in gamedata:
			print(gamedata["gameinfo"])
			ticks = gamedata["ticks"]
			loadgame()
		else:
			$error_popup/error_title/error_text_label.text = "Make sure JSON contains gameinfo and ticks fields"
			$error_popup.popup_centered()
			
	else:  # If parse has errors
		$error_popup/error_title/error_text_label.text = "Error parsing JSON!"
		$error_popup.popup_centered()

func _on_get_file_button_pressed():
	$FileDialog.popup_centered()

func _on_run_all_button_pressed():
	runall_ticks()

func _on_last_tick_button_pressed():
	advance_tick(-1)

func _on_next_tick_button_pressed():
	advance_tick(1)

func _on_FileDialog_file_selected(path):
	$filepath_entry.text = path

func _on_error_ok_button_pressed():
	$error_popup.hide()
