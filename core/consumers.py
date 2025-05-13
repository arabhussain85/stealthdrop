import json
import uuid
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

# In-memory store for connected devices
connected_devices = {}

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create a unique device_id for each device and get the client's IP address
        self.device_id = str(uuid.uuid4())
        self.ip = self.scope["client"][0]
        
        # Accept the WebSocket connection
        await self.accept()

        # Register the device in the connected devices list
        connected_devices[self.device_id] = {
            "device_id": self.device_id,
            "ip": self.ip,
            "platform": "Unknown",  # Default platform, will be updated later
            "name": "Unnamed Device",  # Default name, will be updated later
            "connected_at": int(time.time())
        }

        # Add device to the group for broadcasting updates
        await self.channel_layer.group_add("devices", self.channel_name)

        # Add device to its own unique group (device-specific group)
        await self.channel_layer.group_add(f"device_{self.device_id}", self.channel_name)

    async def disconnect(self, close_code):
        # Clean up when the device disconnects
        if self.device_id in connected_devices:
            del connected_devices[self.device_id]

        # Remove device from the groups
        await self.channel_layer.group_discard("devices", self.channel_name)
        await self.channel_layer.group_discard(f"device_{self.device_id}", self.channel_name)

        # Broadcast updated device list to all connected devices
        await self.channel_layer.group_send(
            "devices",
            {
                "type": "broadcast_devices"
            }
        )

    async def receive(self, text_data):
        # Parse the incoming message
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "update_info":
            # Update device information (platform, name)
            platform = data.get("platform", "Unknown")
            name = data.get("name", "Unnamed Device")
            connected_devices[self.device_id]["platform"] = platform
            connected_devices[self.device_id]["name"] = name

            # Broadcast updated device list to all connected devices
            await self.channel_layer.group_send(
                "devices",
                {
                    "type": "broadcast_devices"
                }
            )

        elif msg_type == "send_message":
            # Handle message sending
            receiver_id = data.get("to")
            content = data.get("content")
            message_type = data.get("message_type", "text")  # message_type can be 'text' or 'url'

            # Check if the receiver is online
            if receiver_id in connected_devices:
                # Send the message to the specific receiver via their group
                await self.channel_layer.group_send(
                    f"device_{receiver_id}",
                    {
                        "type": "receive_message",
                        "from": self.device_id,
                        "message_type": message_type,
                        "content": content
                    }
                )
            else:
                # Send error message to the sender if receiver is offline
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"Device {receiver_id} is not online."
                }))

    async def broadcast_devices(self, event):
        # Send the updated list of connected devices to all clients
        await self.send(text_data=json.dumps({
            "type": "devices_list",
            "devices": list(connected_devices.values())
        }))

    async def receive_message(self, event):
        # Send the incoming message to the receiver device
        await self.send(text_data=json.dumps({
            "type": "incoming_message",
            "from": event["from"],
            "message_type": event["message_type"],
            "content": event["content"]
        }))
