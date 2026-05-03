from app.agent.controller import Controller

if __name__ == "__main__":

    controller = Controller()

    goal = "Create a python file that prints hello, run it, and save output"
    goal_1 = "Create a FastAPI app with one endpoint and run it"
    goal_2 = "Create a FastAPI app that is a project management system all required endpoints and run tests and tell me the result in a file named test_result.txt"

    controller.run(goal_2)