import json

from socketify import App, OpCode, CompressOptions
from socketify.asgi import ws_open


def websocketGateway(ws):
    print("WebSocket Gateway detected and initialized.")
    ws.send("WebSocket connection established.", OpCode.TEXT)

def ws_message(ws, message, opcode):
    if opcode != OpCode.TEXT:
        ws.send(json.dump({
            "error": "Unsupported message type. Only text messages are accepted."
        }), OpCode.TEXT)
        return
    else:
        try:
            data = json.loads(message)
            print("Received data: ", data)

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
    app.listen(3000, lambda: print("Server is running on http://localhost:3000"))
    app.run()