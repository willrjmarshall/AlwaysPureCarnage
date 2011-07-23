import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement


# Constants. Tweaking these would let us work with different grid sizes or different templates

#Index of the columns used for VU display
LEFT_COLUMN_VUS = [2, 3]
RIGHT_COLUMN_VUS = [6, 7]
# Which channels we are monitoring for RMS
LEFT_SOURCE = 2
RIGHT_SOURCE  = 6

# Grid size
CLIP_GRID_X = 8
CLIP_GRID_Y = 5

# Velocity values for clip colours. Different on some devices
LED_RED = 3
LED_ON = 127
LED_OFF = 0
LED_ORANGE = 5

# Scaling constants. Narrows the db range we display to 0db-21db or thereabouts
CHANNEL_SCALE_MAX = 0.92
CHANNEL_SCALE_MIN = 0.52
CHANNEL_SCALE_INCREMENTS = 10

MASTER_SCALE_MAX = 0.92
MASTER_SCALE_MIN = 0.52
MASTER_SCALE_INCREMENTS = 5

class VUMeter():
  'represents a single VU to store RMS values etc in'
  def __init__(self, parent, track, matrix, top, bottom, increments):
    self.parent = parent
    self.track = track
    self.matrix = matrix
    self.top = top
    self.bottom = bottom
    self.multiplier = calculate_multiplier(top, bottom, increments)

  def observe(self):
    level = self.scale_vu(rms_level)
    if level != self.current_level:
      self.current_level = level
      self.parent.set_leds(self.matrix, level) 

    # Perform the scaling as per params. We reduce the range, then round it out to integers
    def scale(self, value):
      if (value > self.top):
        value = self.top
      elif (value < self.bottom):
        value = self.bottom
      value = value - self.bottom
      value = value * self.multiplier #float, scale 0-10
      return int(round(value))
    
    def calculate_multiplier(top, bottom, increments):
      return (increments / (top - bottom))


class VUMeters(ControlSurfaceComponent):
    'standalone class used to handle VU meters'

    def __init__(self, parent):
        # Boilerplate
        ControlSurfaceComponent.__init__(self)
        self._parent = parent

        # Default the L/R/Master levels to 0
        self._meter_level = 0
        self._left_level = 0
        self._right_level = 0

        # We don't start clipping
        self._clipping = False

        # The tracks we'll be pulling L and R RMS from
        self._left_track = self.song().tracks[LEFT_SOURCE]
        self._right_track = self.song().tracks[RIGHT_SOURCE]
        
        # Get ourselves a nice array of the columns of buttons we want to make blink
        self.setup_button_matrixes()

        #setup classes
        self.left_meter = VUMeter(self, parent, self._left_track, 
                                  self._left_matrix, CHANNEL_SCALE_MAX, 
                                  CHANNEL_SCALE_MIN, CHANNEL_SCALE_INCREMENTS)
        self.right_meter = VUMeter(self, parent, self._right_track, 
                                  self._right_matrix, CHANNEL_SCALE_MAX, 
                                  CHANNEL_SCALE_MIN, CHANNEL_SCALE_INCREMENTS)

        # Listeners!
        self._left_track.add_output_meter_left_listener(self.left_meter.observe)
        #self.song().master_track.add_output_meter_right_listener(self.observe_master_vu)
        #self._left_track.add_output_meter_left_listener(self.observe_left_vu)
        #self._right_track.add_output_meter_left_listener(self.observe_right_vu)

    # If you fail to kill the listeners on shutdown, Ableton stores them in memory and punches you in the face
    def disconnect(self):
        self.song().master_track.remove_output_meter_right_listener(self.observe_master_vu)
        self._left_track.remove_output_meter_left_listener(self.observe_left_vu)
        self._right_track.remove_output_meter_left_listener(self.observe_right_vu)

    # Called when the Master clips. Makes the entire clip grid BRIGHT RED 
    #def clip_warning(self):
    #  for row_index in range(CLIP_GRID_Y):
    #    row = self._parent._button_rows[row_index]
    #    for button_index in range(CLIP_GRID_X):
    #      button = row[button_index]
    #      # Passing True to send_value forces it to happen even when the button in question is MIDI mapped
    #      button.send_value(LED_RED, True)

    # Iterate through every column in the matrix, light up the LEDs based on the level
    # Level for channels is scaled to 10 cos we have 10 LEDs
    # Top two LEDs are red, the next is orange
    def set_leds(self, matrix, level):
        for column in matrix:
          for index in range(10):
            button = column[index] 
            if index >= (10 - level): 
              if index < 1:
                button.send_value(LED_RED, True)
              elif index < 2:
                button.send_value(LED_ORANGE, True)
              else:
                button.send_value(LED_ON, True)
            else:
              button.send_value(LED_OFF, True)

    # Create matrix of columns, used to display VU. Can have multiple columns for added pretty
    def setup_button_matrixes(self):
        self._left_matrix = [[],[]]
        self._right_matrix = [[],[]]
        self.setup_matrix(self._left_matrix, LEFT_COLUMN_VUS)
        self.setup_matrix(self._right_matrix, RIGHT_COLUMN_VUS)

    # Goes from top to bottom: so clip grid, then stop, then select, then activator/solo/arm
    def setup_matrix(self, matrix, const):
        for index, column_index in enumerate(const):
          column = matrix[index]
          for row_index in range(CLIP_GRID_Y):
            column.append(self._parent._button_rows[row_index][column_index])
          strip = self._parent._mixer.channel_strip(column_index)
          column.append(self._parent._track_stop_buttons[column_index])
          column.extend([strip._select_button, strip._mute_button, strip._solo_button, strip._arm_button])

    # boilerplate
    def update(self):
        pass

    def on_enabled_changed(self):
        self.update()

    def on_selected_track_changed(self):
        self.update()

    def on_track_list_changed(self):
        self.update()

    def on_selected_scene_changed(self):
        self.update()

    def on_scene_list_changed(self):

        self.update()








