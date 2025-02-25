import bpy
import websockets
import asyncio
import json
from mathutils import Vector, Euler
import math

# Dictionary to keep track of all empties
empties = {}

async def handle_websocket_data():
    uri = "ws://your_websocket_server:port"
    
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                # Receive data from websocket
                data = await websocket.recv()
                data = json.loads(data)
                
                # Extract data
                obj_id = data['id']
                action = data['appear/disappear']
                rotation = data['rotation']  # Assuming [x, y, z] in radians
                translation = data['translation']  # Assuming [x, y, z]
                
                # Handle the data in Blender's main thread
                bpy.app.timers.register(
                    lambda: update_empty(obj_id, action, rotation, translation)
                )
                
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

def update_empty(obj_id, action, rotation, translation):
    if action == "appear":
        if obj_id not in empties:
            # Create new empty if it doesn't exist
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            empty = bpy.context.active_object
            empty.name = f"Empty_{obj_id}"
            empties[obj_id] = empty
            
        # Update empty position and rotation
        empty = empties[obj_id]
        empty.location = Vector(translation)
        empty.rotation_euler = Euler(rotation)
        
    elif action == "disappear":
        if obj_id in empties:
            # Remove empty
            empty = empties[obj_id]
            bpy.data.objects.remove(empty, do_unlink=True)
            del empties[obj_id]
    
    return None

# Start the WebSocket client
def start_websocket_client():
    asyncio.run(handle_websocket_data())

# Register the WebSocket client as a modal operator
class WebSocketOperator(bpy.types.Operator):
    bl_idname = "wm.websocket_operator"
    bl_label = "WebSocket Operator"
    
    def execute(self, context):
        start_websocket_client()
        return {'FINISHED'}

# Register the operator
def register():
    bpy.utils.register_class(WebSocketOperator)

def unregister():
    bpy.utils.unregister_class(WebSocketOperator)

if __name__ == "__main__":
    register()
    # Run the operator
    bpy.ops.wm.websocket_operator()

