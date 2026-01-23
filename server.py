import asyncio
import json
import logging
from websockets import serve, WebSocketServerProtocol, ConnectionClosedOK
from config import Config
from servo import TrashcanLidController, MovementController

config = Config()

# --- LIDS ---
lid_plastic = TrashcanLidController(
    1,
    config.TRASHCAN_LID_1_PWM,
    config.TRASHCAN_LID_5V_1,
    config.TRASHCAN_LID_1_GND
)
lid_paper = TrashcanLidController(
    2,
    config.TRASHCAN_LID_2_PWM,
    config.TRASHCAN_LID_5V_2,
    config.TRASHCAN_LID_2_GND
)
lid_glass = TrashcanLidController(
    3,
    config.TRASHCAN_LID_3_PWM,
    config.TRASHCAN_LID_5V_3,
    config.TRASHCAN_LID_3_GND
)

lids = {
    1: lid_plastic,
    2: lid_paper,
    3: lid_glass
}

# --- MOVEMENT ---
movement = MovementController(
    config.DIR_ENGINE_LEFT,
    config.DIR_ENGINE_RIGHT,
    config.PWM_ENGINE_LEFT,
    config.PWM_ENGINE_RIGHT,
    config.GND_ENGINE
)

# --- STATE ---
currentCommand = "STOP"
MOVE_INTERVAL = 0.05  # 20 Hz motor refresh

# reduce noisy handshake tracebacks
logging.getLogger("websockets.server").setLevel(logging.WARNING)
logging.getLogger("websockets.protocol").setLevel(logging.WARNING)


# ================= CONTROL LOOP =================

async def movement_loop():
    global currentCommand

    while True:
        match currentCommand:
            case "LEFT":
                movement.turn_left()
            case "RIGHT":
                movement.turn_right()
            case "FORWARD":
                movement.move_forward()
            case "BACKWARD":
                movement.move_backward()
            case "STOP":
                movement.stop()
        await asyncio.sleep(MOVE_INTERVAL)


# ================= EVENT HANDLER =================

async def handle_event(websocket, event, data):
    global currentCommand

    match event:

        case "TEST_CONNECTION":
            await websocket.send(json.dumps({
                "event": "TEST_CONNECTION_RESPONSE",
                "message": "Connection is active."
            }))

        case "MOVE":
            direction = data.get("direction")

            if direction not in {"LEFT", "RIGHT", "FORWARD", "BACKWARD", "STOP"}:
                await websocket.send(json.dumps({
                    "error": "Unknown move direction."
                }))
                return

            currentCommand = direction

        case "OPEN_TRASHCAN" | "CLOSE_TRASHCAN":
            trashLid = data.get("lid")

            if trashLid not in lids:
                await websocket.send(json.dumps({
                    "error": "Invalid trashcan lid identifier."
                }))
                return

            lid = lids[trashLid]

            if event == "OPEN_TRASHCAN":
                await lid.open_lid()
            else:
                await lid.close_lid()

            await websocket.send(json.dumps({
                "status": "ok",
                "lid": trashLid,
                "action": event
            }))

        case _:
            await websocket.send(json.dumps({
                "error": "Unknown event type."
            }))


# ================= WEBSOCKET =================

async def handler(websocket: WebSocketServerProtocol):
    global currentCommand

    print("WebSocket client connected.")
    await websocket.send(json.dumps({
        "message": "WebSocket connection established."
    }))

    try:
        async for message in websocket:
            data = json.loads(message)
            print("Received:", data)

            event = data.get("event")
            if not event:
                await websocket.send(json.dumps({
                    "error": "Missing event field."
                }))
                continue

            await handle_event(websocket, event, data)

    except ConnectionClosedOK:
        print("Client disconnected – stopping robot")
        currentCommand = "STOP"
        movement.stop()

    except Exception as e:
        logging.exception("WebSocket handler error: %s", e)


# ================= MAIN =================

async def main():
    asyncio.create_task(movement_loop())

    async with serve(handler, "0.0.0.0", 3000):
        print("Server running on 0.0.0.0:3000")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down")
