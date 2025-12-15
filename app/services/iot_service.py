# app/services/iot_service.py
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

class IoTService:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_IOT_HUB_CONNECTION_STRING")
        self.registry_manager = IoTHubRegistryManager(self.connection_string)
    
    def receive_device_data(self, device_id, data):

        pass
    
    def send_to_device(self, device_id, command):
        # Send commands to IoT device
        method = CloudToDeviceMethod(method_name=command)
        self.registry_manager.invoke_device_method(device_id, method)