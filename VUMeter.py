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
CHANNEL_SCALE_MAX = 0.9
CHANNEL_SCALE_MIN = 0.5
CHANNEL_SCALE_MULTIPLY = 25

MASTER_SCALE_MAX = 0.92
MASTER_SCALE_MIN = 0.52
MASTER_SCALE_MULTIPLY = 12.5

class VUMeter(ControlSurfaceComponent):
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

        # Listeners!
        self.song().master_track.add_output_meter_right_listener(self.observe_master_vu)
        self._left_track.add_output_meter_left_listener(self.observe_left_vu)
        self._right_track.add_output_meter_left_listener(self.observe_right_vu)

    # If you fail to kill the listeners on shutdown, Ableton stores them in memory and punches you in the face
    def disconnect(self):
        self.song().master_track.remove_output_meter_right_listener(self.observe_master_vu)
        self._left_track.remove_output_meter_left_listener(self.observe_left_vu)
        self._right_track.remove_output_meter_left_listener(self.observe_right_vu)

    # Scales floats from 0-1 to integers from 0-10, with some cutoffs
    def scale_vu(self, value):
      return self.scale(value, CHANNEL_SCALE_MAX, CHANNEL_SCALE_MIN, CHANNEL_SCALE_MULTIPLY)
    
    # Scales floats from 0-1 to integers from 0-5, with some cutoffs
    def scale_master(self, value):
      return self.scale(value, MASTER_SCALE_MAX, MASTER_SCALE_MIN, MASTER_SCALE_MULTIPLY)

    # Perform the scaling as per params. We reduce the range, then round it out to integers
    def scale(self, value, top, bottom, multiplier):
      if (value > top):
        value = top
      elif (value < bottom):
        value = bottom
      value = value - bottom
      value = value * multiplier #float, scale 0-10
      return int(round(value))

    def observe_master_vu(self):
        master_level = self.song().master_track.output_meter_right 
        if master_level >= 0.92:
          self._clipping = True
          self.clip_warning()
        else:
          if self._clipping:
            self._parent.refresh_state()
            self._clipping = False
          self._meter_level = self.scale_master(master_level)
          self.set_master_leds()


    # Observes changes in the RMS of tracks, sets their level as an integer and passes it through to led code
    def observe_vu(self, matrix, track):
      # If we are currently clipping, EVERYTHING is red and no VUs are shown
      if self._clipping == False:
        level = self.scale_vu(track.output_meter_left)
        self.set_leds(matrix, level)

    # Python doesn't seem to have closures that'll make this nicer. FAIL PYTHON.
    def observe_left_vu(self):
      self.observe_vu(self._left_matrix, self._left_track)

    def observe_right_vu(self):
      self.observe_vu(self._right_matrix, self._right_track)

    # Called when the Master clips. Makes the entire clip grid BRIGHT RED 
    def clip_warning(self):
      for row_index in range(CLIP_GRID_Y):
        row = self._parent._button_rows[row_index]
        for button_index in range(CLIP_GRID_X):
          button = row[button_index]
          # Passing True to send_value forces it to happen even when the button in question is MIDI mapped
          button.send_value(LED_RED, True)

    # Light up the scene launch buttons based on current Master level
    def set_master_leds(self):
        for scene_index in range(CLIP_GRID_Y):
            scene = self._parent._session.scene(scene_index)
            if scene_index >= (CLIP_GRID_Y - self._meter_level):
              scene._launch_button.send_value(LED_ON, True)
            else:
              scene._launch_button.send_value(LED_OFF, True)
  
    # Iterate through every column in the matrix, light up the LEDs based on the level
    # Level for channels is scaled to 10 cos we have 10 LEDs
    # Top two LEDs are red, the next is orange
    def set_leds(self, matrix, level):
        for column_index in range(len(matrix)):
          for index in range(10):
            button = matrix[column_index][index] 
            if index >= (10 - level): 
              if index < 2:
                button.send_value(LED_RED, True)
              elif index < 4:
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
          column.append(strip._select_button)
          column.append(strip._mute_button)
          column.append(strip._solo_button)
          column.append(strip._arm_button)

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









