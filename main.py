import uvicorn



from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
with open("htmldirectory/home.html", 'r') as f:
    html = f.read()

"""
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


"""
const drawobs = [
            {type:"poly", parameters:[points, color, width]}, 
            {type:"rect", parameters:[rect, color, 0]},
            
            ];
draw = [ [type, [params] ]    ]
"""
class user:
    def __init__(self):
        self.name = 'bob'
        self.draw = []

    def get_draw(self):
        x = '['
        num = 0
        for i in self.draw:
            num += 1
            x += '{"type":"' + i[0] + '", "parameters":['
            num2 = 0
            for b in i[1]:
                num2 += 1
                print(b)
                x += str(b)
                if num2 != len(i[1]):
                    x += ', '
            x += ']}'
            if num != len(self.draw):
                x += ', '
        x += ']'

        return x


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

class connection:
    def __init__(self, websocket, client_id):
        self.id = client_id
        self.websocket = websocket
        self.user = user()

    def send_draw_info(self):
        return self.user.get_draw()

    def get_input(self, data):
        print(data)
        # self.user.handle_input(data)


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    connect = connection(websocket, client_id)
    try:
        while True:
            await manager.send_personal_message(connect.send_draw_info(), websocket)

            data = await websocket.receive_text()
            data = json.loads(data)
            connect.get_input(data)
            await manager.send_personal_message(connect.send_draw_info(), websocket)
            # await manager.broadcast(f"Client #{client_id}  says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
