from app.agent.controller import Controller

if __name__ == "__main__":

    controller = Controller()

    goal = "Create a python file that prints hello, run it, and save output"
    goal_1 = "Create a FastAPI app with one endpoint and run it"

    controller.run(goal_1)