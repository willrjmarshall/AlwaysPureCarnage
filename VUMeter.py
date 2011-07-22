import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement

class VUMeter(ControlSurfaceComponent):
    'standalone class used to handle VU meters'

    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
        self._meter_level = 0
        self._left_level = 0
        self._right_level = 0


        self._clipping = False

        self._left_track = self.song().tracks[2]
        self._right_track = self.song().tracks[6]
        
        self.setup_button_matrixes()

        self.song().master_track.add_output_meter_right_listener(self.observe_master_vu)
        self._left_track.add_output_meter_left_listener(self.observe_left_vu)
        self._right_track.add_output_meter_left_listener(self.observe_right_vu)

    def disconnect(self):
        self.song().master_track.remove_output_meter_right_listener(self.observe_master_vu)
        self._left_track.remove_output_meter_left_listener(self.observe_left_vu)
        self._right_track.remove_output_meter_left_listener(self.observe_right_vu)

    def observe_master_vu(self):
        master_level = self.song().master_track.output_meter_right 

        if master_level >= 0.92:
          self._clipping = True
          self.clip_warning()
        else:
          if self._clipping:
            self._parent.refresh_state()
            self._clipping = False

          if (master_level > 0.92):
            master_level = 0.92
          elif (master_level < 0.52):
            master_level = 0.52
          master_level = master_level - 0.52
          master_level = master_level * 12.5 #float, scale 0-5
          self._meter_level = int(round(master_level))
          self.set_master_leds()


    def observe_left_vu(self):
        if self._clipping == False:
          left_level = self._left_track.output_meter_left
          if (left_level > 0.9):
            left_level = 0.9
          elif (left_level < 0.4):
            left_level = 0.4
          left_level = left_level - 0.4
          left_level = left_level * 20 #float, scale 0-10
          self._left_level = int(round(left_level))
          self.set_leds(self._left_matrix, self._left_level)

    def observe_right_vu(self):
        if self._clipping == False:
          right_level = self._right_track.output_meter_left
          if (right_level > 0.9):
            right_level = 0.9
          elif (right_level < 0.4):
            right_level = 0.4
          right_level = right_level - 0.4
          right_level = right_level * 20 #float, scale 0-10
          self._right_level = int(round(right_level))
          self.set_leds(self._right_matrix, self._right_level)

    def clip_warning(self):
      for row_index in range(5):
        row = self._parent._button_rows[row_index]
        for button_index in range(8):

          button = row[button_index]
          button.send_value(3, True)


    def set_master_leds(self):
        for scene_index in range(5):
            scene = self._parent._session.scene(scene_index)
            if scene_index >= (5 - self._meter_level):
              scene._launch_button.send_value(127, True)
            else:
              scene._launch_button.send_value(0, True)
  
    def set_leds(self, matrix, level):
        for column_index in range(2):
          for index in range(10):

            self._parent.log_message(str(column_index))
            self._parent.log_message(str(index))

            button = matrix[column_index][index] 
            if index >= (10 - level): 
              if index < 2:
                button.send_value(3, True)
              elif index < 4:
                button.send_value(5), True
              else:
                button.send_value(127, True)
            else:
              button.send_value(0, True)


    def setup_button_matrixes(self):
        self._left_matrix = [[],[]] # Matrix of all the buttons for the left channel
        self._right_matrix = [[],[]] # Matrix of all the buttons for the left channel
        
        for button_index in range(5):
          self._left_matrix[0].append(self._parent._button_rows[button_index][2])
          self._left_matrix[1].append(self._parent._button_rows[button_index][3])
          self._right_matrix[0].append(self._parent._button_rows[button_index][6])
          self._right_matrix[1].append(self._parent._button_rows[button_index][7])

        for column_index in range(2):
          column = self._left_matrix[column_index]
          strip = self._parent._mixer.channel_strip(2 + column_index)
          column.append(self._parent._track_stop_buttons[2 + column_index])
          column.append(strip._select_button)
          column.append(strip._mute_button)
          column.append(strip._solo_button)
          column.append(strip._arm_button)

          column = self._right_matrix[column_index]
          strip = self._parent._mixer.channel_strip(6 + column_index)
          column.append(self._parent._track_stop_buttons[6 + column_index])
          column.append(strip._select_button)
          column.append(strip._mute_button)
          column.append(strip._solo_button)
          column.append(strip._arm_button)

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









