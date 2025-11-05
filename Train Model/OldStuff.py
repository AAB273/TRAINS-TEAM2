"""
    def _process_message(self, message, source_ui_id):
        Process incoming messages and update train state
        try:
            print(f"Received message from {source_ui_id}: {message}")

            command = message.get('command')
            value = message.get('value')
            
            if command == 'set_power':
                self.current_train.last_power_command = self.current_train.power_command
                self.current_train.set_power_command(value)
            elif command == 'set_right_door':
                if value == 'open':
                    self.current_train.set_right_door(1)
                elif value == 'close':
                    self.current_train.set_right_door(0)
            elif command == 'set_left_door':
                if value == 'open':
                    self.current_train.set_left_door(1)
                elif value == 'close':
                    self.current_train.set_left_door(0)
            elif command == 'set_headlights':
                if value == 'on':
                    self.current_train.set_headlights(1)
                else:
                    self.current_train.set_headlights(0)
            elif command == 'set_interior_lights':
                if value == 'on':
                    self.current_train.set_interior_lights(1)
                elif value == 'off':
                    self.current_train.set_interior_lights(0)
            elif command == 'emergency_brake':
                if value == 'on':
                    self.emergency_brake_activated()
                else:
                    self.current_train.set_emergency_brake(0)
            elif command == 'set_service_brake':
                if value == 'on':
                    self.current_train.set_service_brake(1)
                else:
                    self.current_train.set_service_brake(0)
            elif command == 'set_passenger_count':
                self.current_train.set_passenger_count(value)
          #  elif command == 'horn':
           #     playsound('C:\Users\wolfm\OneDrive - University of Pittsburgh\Desktop\Trains GIT Location\TRAINS-TEAM2\Train Model\diesel-horn-02-98042.mp3')
            elif command == 'set_speed_limit':
                self.current_train.set_speed_limit(value)
            elif command == 'set_elevation':
                self.current_train.set_elevation(value)
            elif command == 'set_grade':
                self.current_train.set_grade(value)
            elif command == 'select_train':
                self.on_train_selected(value)
            elif command == 'set_temperature':
                target_temp = value
                self._animate_temperature_change(target_temp)
            elif command == 'set_station':
                self.current_train.set_station(value)
            elif command == 'set_time_to_station':
                self.current_train.set_time_to_station(value)
            elif command == 'deploy_train':
                train_id = value
                train = self.train_manager.get_train(train_id)
                if train:
                    train.deployed = True
                    print(f"Deployed train {train_id}")
                    self._socket_refresh_train_selector()
                    train.calculate_force_speed_acceleration_()
            elif command == 'undeploy_train':
                train_id = value
                train = self.train_manager.get_train(train_id)
                if train:
                    train.deployed = False
                    print(f"Undeployed train {train_id}")
                    self._socket_refresh_train_selector()
            elif command == 'deploy_all':
                for train_id in range(1, 15):
                    train = self.train_manager.get_train(train_id)
                    if train:
                        train.deployed = True
                        self.current_train.calculate_force_speed_acceleration_()
                print("Deployed all trains")
                self._socket_refresh_train_selector()
            elif command == 'undeploy_all':
                for train_id in range(1, 15):
                    train = self.train_manager.get_train(train_id)
                    if train:
                        train.deployed = False
                print("Undeployed all trains")
                self._socket_refresh_train_selector()
            elif command == 'refresh_trains':
                self._socket_refresh_train_selector()
            
            # Force UI update
            self.update_ui_from_train(self.current_train)
            
        except Exception as e:
            print(f"Error processing message: {e}")
    """