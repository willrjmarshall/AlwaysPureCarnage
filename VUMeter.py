import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class VUMeter(ControlSurfaceComponent):
    'standalone class used to handle VU meters'

    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
        self._meter_level = 0
        self._left_level = 0
        self._right_level = 0


        self._clipping = False

        self._left_track = self.song().tracks[0]
        self._right_track = self.song().tracks[1]
        
        self.setup_button_matrixes()

        self.song().master_track.add_output_meter_level_listener(self.observe_master_vu)
        self._left_track.add_output_meter_level_listener(self.observe_left_vu)
        self._right_track.add_output_meter_level_listener(self.observe_right_vue)

        parent.log_message(str(self.song().master_track.output_meter_level))

    def disconnect(self):
        self.song().master_track.remove_output_meter_level_listener(self.observe_master_vu)
        self._left_track.remove_output_meter_level_listener(self.observe_left_vu)

    def observe_master_vu(self):
        master_level = self.song().master_track.output_meter_level 

        if master_level >= 0.92:
          self._clipping = True
          self.clip_warning()
        else:
          # reset
          if self._clipping:
            self._parent._session._reassign_tracks()
            self._parent._session._reassign_scenes()
            self._clipping = False

          if (master_level > 0.9):
            master_level = 0.9
          elif (master_level < 0.4):
            master_level = 0.4
          master_level = master_level - 0.4
          master_level = master_level * 10.0 #float, scale 0-5
          self._meter_level = int(round(master_level))
          self.set_master_leds()


    def observe_left_vu(self):
        if self._clipping == False:
          left_level = self._left_track.output_meter_level
          if (left_level > 0.9):
            left_level = 0.9
          elif (left_level < 0.4):
            left_level = 0.4
          left_level = left_level - 0.4
          left_level = left_level * 20 #float, scale 0-5
          self._left_level = int(round(left_level))
          self.set_leds(self._left_matrix, self._left_level)

    def observe_right_vue(self):
        if self._clipping == False:
          right_level = self._right_track.output_meter_level
          if (right_level > 0.9):
            right_level = 0.9
          elif (right_level < 0.4):
            right_level = 0.4
          right_level = right_level - 0.4
          right_level = right_level * 20 #float, scale 0-5
          self._right_level = int(round(right_level))
          self.set_leds(self._right_matrix, self._right_level)

    def clip_warning(self):
      self._parent.log_message("Clipping")
      for row_index in range(5):
        row = self._parent._button_rows[row_index]
        for button_index in range(8):
          button = row[button_index]
          button.send_value(3)


    def set_master_leds(self):
        for scene_index in range(5):
            scene = self._parent._session.scene(scene_index)
            if scene_index >= (5 - self._meter_level):
              scene._launch_button.turn_on()
            else:
              scene._launch_button.turn_off()
  
    def set_leds(self, matrix, level):
        for index in range(10):
          button = matrix[index] 
          if index >= (10 - level): 
            if index < 2:
              button.send_value(3)
            elif index < 4:
              button.send_value(5)
            else:
              button.turn_on()
          else:
            button.turn_off()

    def setup_button_matrixes(self):
        self._left_matrix = [] # Matrix of all the buttons for the left channel
        self._right_matrix = [] # Matrix of all the buttons for the left channel
        
        for button_index in range(5):
          self._left_matrix.append(self._parent._button_rows[button_index][2])
          self._right_matrix.append(self._parent._button_rows[button_index][6])
  
        strip = self._parent._mixer.channel_strip(2)
        self._left_matrix.append(self._parent._track_stop_buttons[2])
        self._left_matrix.append(strip._select_button)
        self._left_matrix.append(strip._mute_button)
        self._left_matrix.append(strip._solo_button)
        self._left_matrix.append(strip._arm_button)

        strip = self._parent._mixer.channel_strip(6)
        self._right_matrix.append(self._parent._track_stop_buttons[6])
        self._right_matrix.append(strip._select_button)
        self._right_matrix.append(strip._mute_button)
        self._right_matrix.append(strip._solo_button)
        self._right_matrix.append(strip._arm_button)


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









