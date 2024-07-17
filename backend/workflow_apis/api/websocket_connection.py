import websocket
import uuid

def open_websocket_connection():
  print('Inside Open websocket connection')
  server_address='34.244.15.18:5000'
  client_id=str(uuid.uuid4())

  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  return ws, server_address, client_id