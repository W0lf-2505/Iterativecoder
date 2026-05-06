from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from threading import Thread
import uuid

from app.agent.controller import Controller

controllers = {}

def get_controller(session_id: str):
    if session_id not in controllers:
        controllers[session_id] = Controller()
    return controllers[session_id]

router = APIRouter()

# in-memory store (fine for now)
active_tasks = {}


@router.post("/run")
def run(goal: str, session_id: str):
    controller = get_controller(session_id)

    task_id = str(uuid.uuid4())

    active_tasks[task_id] = {
        "logs": [],
        "status": "running"
    }

    def run_task():
        controller.run(goal, callback=lambda msg: active_tasks[task_id]["logs"].append(msg))
        active_tasks[task_id]["status"] = "completed"

    Thread(target=run_task).start()

    return {
        "task_id": task_id,
        "session_id": session_id
    }

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