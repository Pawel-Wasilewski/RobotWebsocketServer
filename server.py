import asyncio
import json
import logging
from websockets import serve, WebSocketServerProtocol, ConnectionClosedOK

from config import Config
from servo import TrashcanLidController, MovementController

# SERVO CONTROLLERS INITIALIZATION (tak jak poprzednio)
lid_plastic = TrashcanLidController(1, None, None)
lid_paper = TrashcanLidController(2, None, None)
lid_glass = TrashcanLidController(3, None, None)

lids = [lid_plastic, lid_paper, lid_glass]
config = Config()
movement = MovementController()

# reduce noisy handshake tracebacks from websockets library
logging.getLogger("websockets.server").setLevel(logging.WARNING)
logging.getLogger("websockets.protocol").setLevel(logging.WARNING)

async def handler(websocket: WebSocketServerProtocol):
    print("WebSocket Gateway detected and initialized.")
    await websocket.send(json.dumps({"message": "WebSocket connection established."}))

    try:
        async for message in websocket:
            # websockets zwraca `str` dla tekstu i `bytes` dla binarnych
            if isinstance(message, (bytes, bytearray)):
                await websocket.send(json.dumps({
                    "error": "Unsupported message type. Only text messages are accepted."
                }))
                continue

            try:
                data = json.loads(message)
                print("Received data:", data)
                event = data.get("event")

                match event:
                    case "TEST_CONNECTION":
                        await websocket.send(json.dumps({
                            "event": "TEST_CONNECTION_RESPONSE",
                            "message": "Connection is active."
                        }))

                    case "MOVE":
                        direction = data.get("direction")
                        match direction:
                            case "LEFT":
                                movement.turn_left()
                                await websocket.send(json.dumps({}))  # TODO: feedback
                            case "RIGHT":
                                movement.turn_right()
                                await websocket.send(json.dumps({}))
                            case "FORWARD":
                                movement.move_forward()
                                await websocket.send(json.dumps({}))
                            case "BACKWARD":
                                movement.move_backward()
                                await websocket.send(json.dumps({}))
                            case "STOP":
                                movement.stop()
                                await websocket.send(json.dumps({}))
                            case _:
                                await websocket.send(json.dumps({"error": "Unknown move direction."}))

                    case "OPEN_TRASHCAN" | "CLOSE_TRASHCAN":
                        trashlid = data.get("lid")
                        # elastyczna walidacja: jeśli NUMBER_OF_TRASHCANS to int -> zakres,
                        # w przeciwnym razie traktujemy to jako kolekcja
                        valid = False
                        if isinstance(getattr(config, "NUMBER_OF_TRASHCANS", None), int):
                            valid = isinstance(trashlid, int) and 0 <= trashlid < config.NUMBER_OF_TRASHCANS
                        else:
                            try:
                                valid = trashlid in config.NUMBER_OF_TRASHCANS
                            except Exception:
                                valid = False

                        if valid:
                            # TODO: implement open/close logic using lids list
                            await websocket.send(json.dumps({}))
                        else:
                            await websocket.send(json.dumps({
                                "error": "Invalid trashcan lid identifier."
                            }))

                    case _:
                        await websocket.send(json.dumps({
                            "error": "Unknown event type."
                        }))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "error": "Invalid JSON format."
                }))

    except ConnectionClosedOK:
        print("WebSocket closed connection")
    except Exception as e:
        logging.exception("WebSocket handler error: %s", e)

async def main():
    async with serve(handler, "0.0.0.0", 3000, max_size=16 * 1024 * 1024, ping_interval=12):
        print("Server running on 0.0.0.0:3000")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down")
