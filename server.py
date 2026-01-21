import json

from socketify import App, OpCode, CompressOptions
from socketify.asgi import ws_open
from config import Config
from servo import TrashcanLidController, MovementController

# SERVO CONTROLLERS INITIALIZATION
lid_plastic = TrashcanLidController(1, None, None)  # TODO: Replace None with actual servo motor instances)
lid_paper = TrashcanLidController(2, None, None)   # TODO: Replace None with actual servo motor instances)
lid_glass = TrashcanLidController(3, None, None)   # TODO: Replace None with actual servo motor instances)

lids = [lid_plastic, lid_paper, lid_glass]
config = Config()
movement = MovementController()  # TODO: Initialize with actual servo motor instances

def websocketGateway(ws):
    print("WebSocket Gateway detected and initialized.")
    ws.send("WebSocket connection established.", OpCode.TEXT)

def ws_message(ws, message, opcode):

    if opcode != OpCode.TEXT:
        ws.send(json.dumps({
            "error": "Unsupported message type. Only text messages are accepted."
        }), OpCode.TEXT)
        return
    else:
        try:
            data = json.loads(message)
            print("Received data: ", data)

            event = data.get("event")
            match event:

                case "TEST_CONNECTION":
                    ws.send(json.dumps({
                        "event": "TEST_CONNECTION_RESPONSE",
                        "message": "Connection is active."
                    }), OpCode.TEXT)

                case "MOVE":
                    direction = data.get("direction")
                    match direction:
                        case "LEFT":
                            movement.turn_left()
                            ws.send(json.dumps({}), OpCode.TEXT) #TODO Implement movement feedback
                        case "RIGHT":
                            movement.turn_right()
                            ws.send(json.dumps({}), OpCode.TEXT) #TODO Implement movement feedback
                        case "FORWARD":
                            movement.move_forward()
                            ws.send(json.dumps({}), OpCode.TEXT) #TODO Implement movement feedback
                        case "BACKWARD":
                            movement.move_backward()
                            ws.send(json.dumps({}), OpCode.TEXT) #TODO Implement movement feedback
                        case "STOP":
                            movement.stop()
                            ws.send(json.dumps({}), OpCode.TEXT) #TODO Implement movement feedback
                        case _:
                            ws.send(json.dumps({})) #TODO Implement error feedback

                case "OPEN_TRASHCAN":
                    trashlid = data.get("lid")
                    if trashlid in config.NUMBER_OF_TRASHCANS:
                        ws.send(json.dumps({})) # TODO Implement trashcan lid opening logic
                    else:
                        ws.send(json.dumps({
                            "error": "Invalid trashcan lid identifier."
                        }), OpCode.TEXT)
                case "CLOSE_TRASHCAN":
                    trashlid = data.get("lid")
                    if trashlid in config.NUMBER_OF_TRASHCANS:
                        ws.send(json.dumps({}))  # TODO Implement trashcan lid opening logic
                    else:
                        ws.send(json.dumps({
                            "error": "Invalid trashcan lid identifier."
                        }), OpCode.TEXT)
                case _:
                    ws.send(json.dumps({
                        "error": "Unknown event type."
                    }), OpCode.TEXT)

        except json.decoder.JSONDecodeError:
            ws.send(json.dumps({
                "error": "Invalid JSON format."
            }), OpCode.TEXT)
            return

def serveServer(app):
    app.ws("/*", {
        'compression': CompressOptions.SHARED_COMPRESSOR,
        'max_payload_length': 16 * 1024 * 1024,
        'idle_timeout': 12,
        'open': ws_open,
        'message': ws_message,
        'drain': lambda ws: print('WebSocket backpressure: %i' % ws.get_buffered_amount()),
        'close': lambda ws, code, message: print('WebSocket closed connection')
    })
    app.any("/", lambda res,req: res.end("Invalid. Please use WebSocket protocol."))

if __name__ == "__main__":
    app = App()
    serveServer(app)
    app.listen(3000, "0.0.0.0")
    print("Server running on 0.0.0.0:3000")
    app.run()
