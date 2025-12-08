from Passenger_UI import TrainModelPassengerGUI

class DebugTrainGUI(TrainModelPassengerGUI):
    def _processMessage(self, message: dict, sourceUiId: str):
        # Log all incoming messages
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        print(f"DEBUG MESSAGE: Source={sourceUiId}, Command={command}, Value={value}, TrainID={train_id}")
        
        # Call original method
        super()._processMessage(message, sourceUiId)

if __name__ == "__main__":
    app = DebugTrainGUI()
    app.run()