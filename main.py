import uvicorn

# python testing

from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
with open("htmldirectory/home.html", 'r') as f:
    html = f.read()

"""
const drawobs = [
            {type:"poly", parameters:[points, color, width]}, 
            {type:"rect", parameters:[rect, color, 0]},
            
            ];
draw = [ [type, [params] ]    ]
"""
# draw = ['rect', [[x, y, width, height], [color ], 0]]


class user:
    def __init__(self):
        self.name = 'bob'
        self.draw = [['fill_screen', [[0, 100, 100]]], ['rect', [[10, 10, 50, 50], [100, 0, 255], 0]]]

    def get_draw(self):
        x = '['
        num = 0
        for i in self.draw:
            num += 1
            x += '{"type":"' + i[0] + '", "parameters":['
            num2 = 0
            for b in i[1]:
                num2 += 1
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


class connections:
    def __init__(self, websocket, client_id, man: ConnectionManager):
        self.man = man
        self.id = client_id
        self.websocket = websocket
        self.get_in = True
        self.send_draw = True
        self.user = user()

    def send_draw_info(self):
        return '["draw", ' + self.user.get_draw() + ']'

    def get_input(self, data):
        print(data)
        # self.user.handle_input(data)


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    connect = connections(websocket, client_id, manager)
    try:
        while True:
            if connect.send_draw is not True and connect.get_in is not True:
                await manager.send_personal_message('["None"]', websocket)
                data = await websocket.receive_text()
            else:
                if connect.get_in:
                    await manager.send_personal_message('["get_input"]', websocket)
                    data = await websocket.receive_text()
                    data = json.loads(data)
                    connect.get_input(data)
                    connect.get_in = False
                    print('data recived')
                if connect.send_draw:
                    await manager.send_personal_message(connect.send_draw_info(), websocket)
                    connect.send_draw = False

    except WebSocketDisconnect:
        manager.disconnect(websocket)




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
