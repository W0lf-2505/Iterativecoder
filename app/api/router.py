from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from threading import Thread
import uuid

from app.agent.controller import Controller

router = APIRouter()

# in-memory store (fine for now)
active_tasks = {}


@router.post("/run")
def run_agent(goal: str):
    task_id = str(uuid.uuid4())

    controller = Controller()

    # store logs per task
    active_tasks[task_id] = {
        "logs": [],
        "status": "running"
    }

    def run():
        try:
            controller.run(goal, callback=lambda msg: active_tasks[task_id]["logs"].append(msg))
            active_tasks[task_id]["status"] = "completed"
        except Exception as e:
            active_tasks[task_id]["logs"].append(str(e))
            active_tasks[task_id]["status"] = "error"

    Thread(target=run).start()

    return {"task_id": task_id}

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    try:
        last_index = 0

        while True:
            task = active_tasks.get(task_id)

            if not task:
                await websocket.send_text("Invalid task ID")
                break

            logs = task["logs"]

            # send new logs only
            if last_index < len(logs):
                new_logs = logs[last_index:]
                for log in new_logs:
                    await websocket.send_text(log)

                last_index = len(logs)

            if task["status"] in ["completed", "error"]:
                await websocket.send_text(f"STATUS: {task['status']}")
                break

    except WebSocketDisconnect:
        print(f"Client disconnected: {task_id}")