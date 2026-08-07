from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Камень, Ножницы, Бумага - Дуэль</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: #e0e0e0; text-align: center; padding-top: 50px; }
        .card { background: #1e1e1e; padding: 25px; border-radius: 10px; display: inline-block; width: 380px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        button { background: #6200ee; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #3700b3; }
        .status { margin: 15px 0; font-weight: bold; color: #bb86fc; }
        input { padding: 10px; width: 80%; margin-bottom: 15px; border-radius: 5px; border: 1px solid #444; background: #2c2c2c; color: #fff; text-align: center; font-size: 16px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎮 Игровая Дуэль</h2>
        <div id="setup">
            <p style="color: #aaa; font-size: 14px; margin-bottom: 15px;">Добро пожаловать! Введите имя и начните игру.</p>
            <input type="text" id="username" placeholder="Ваш никнейм" value="Игрок"><br>
            <button onclick="joinQueue()">Начать дуэль</button>
        </div>
        <div id="game" style="display: none;">
            <div class="status" id="gameStatus">Ожидание соперника...</div>
            <div id="choices" style="display: none;">
                <p>Сделайте выбор:</p>
                <button onclick="makeChoice('rock')">🪨 Камень</button>
                <button onclick="makeChoice('scissors')">✂️ Ножницы</button>
                <button onclick="makeChoice('paper')">📄 Бумага</button>
            </div>
            <div id="result" style="margin-top: 15px; font-size: 18px; line-height: 1.5;"></div>
            <button id="restartBtn" style="display: none; margin-top: 15px; background: #03dac6; color: #000;" onclick="location.reload()">Сыграть еще</button>
        </div>
    </div>

    <script>
        let ws;
        let myName = "";

        function joinQueue() {
            myName = document.getElementById("username").value || "Игрок";
            document.getElementById("setup").style.display = "none";
            document.getElementById("game").style.display = "block";

            ws = new WebSocket("ws://" + window.location.host + "/ws");

            ws.onopen = function() {
                ws.send(JSON.stringify({action: "join", name: myName}));
            };

            ws.onmessage = function(event) {
                let data = JSON.parse(event.data);
                handleServerMessage(data);
            };
        }

        function makeChoice(choice) {
            ws.send(JSON.stringify({action: "choice", choice: choice}));
            document.getElementById("choices").style.display = "none";
            document.getElementById("gameStatus").innerText = "Выбор принят. Ожидание соперника...";
        }

        function handleServerMessage(data) {
            const statusEl = document.getElementById("gameStatus");
            const choicesEl = document.getElementById("choices");
            const resultEl = document.getElementById("result");

            if (data.type === "waiting") {
                statusEl.innerText = data.message;
            } else if (data.type === "start") {
                statusEl.innerText = "Соперник найден: " + data.opponent + "!";
                choicesEl.style.display = "block";
                resultEl.innerText = "";
            } else if (data.type === "game_over") {
                choicesEl.style.display = "none";
                statusEl.innerText = "Раунд завершен!";
                resultEl.innerHTML = `<b>${data.result}</b><br><span style="font-size: 14px; color: #aaa;">Вы: ${data.my_choice} | Соперник: ${data.opp_choice}</span>`;
                document.getElementById("restartBtn").style.display = "inline-block";
            }
        }
    </script>
</body>
</html>
"""

waiting_player = None
active_matches = {}

class Match:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.p1_choice = None
        self.p2_choice = None

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global waiting_player
    await websocket.accept()
    
    try:
        while True:
            data_raw = await websocket.receive_text()
            data = json.loads(data_raw)
            action = data.get("action")

            if action == "join":
                player_name = data.get("name", "Игрок")
                
                if waiting_player is None:
                    waiting_player = {"ws": websocket, "name": player_name}
                    await websocket.send_text(json.dumps({"type": "waiting", "message": "Поиск соперника в очереди..."}))
                else:
                    p1 = waiting_player
                    p2 = {"ws": websocket, "name": player_name}
                    waiting_player = None

                    match = Match(p1, p2)
                    active_matches[p1["ws"]] = match
                    active_matches[p2["ws"]] = match

                    await p1["ws"].send_text(json.dumps({"type": "start", "opponent": p2["name"]}))
                    await p2["ws"].send_text(json.dumps({"type": "start", "opponent": p1["name"]}))

            elif action == "choice":
                choice = data.get("choice")
                match = active_matches.get(websocket)
                if match:
                    if websocket == match.p1["ws"]:
                        match.p1_choice = choice
                    else:
                        match.p2_choice = choice

                    if match.p1_choice and match.p2_choice:
                        c1, c2 = match.p1_choice, match.p2_choice
                        
                        if c1 == c2:
                            res_p1 = res_p2 = "Ничья!"
                        elif ((c1 == "rock" and c2 == "scissors") or 
                              (c1 == "scissors" and c2 == "paper") or 
                              (c1 == "paper" and c2 == "rock")):
                            res_p1 = "Победа!"
                            res_p2 = "Поражение!"
                        else:
                            res_p1 = "Поражение!"
                            res_p2 = "Победа!"

                        await match.p1["ws"].send_text(json.dumps({
                            "type": "game_over", "result": res_p1, "my_choice": c1, "opp_choice": c2
                        }))
                        await match.p2["ws"].send_text(json.dumps({
                            "type": "game_over", "result": res_p2, "my_choice": c2, "opp_choice": c1
                        }))

    except WebSocketDisconnect:
        if waiting_player and waiting_player["ws"] == websocket:
            waiting_player = None
        if websocket in active_matches:
            del active_matches[websocket]