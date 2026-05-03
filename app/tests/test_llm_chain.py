from app.agent.controller import Controller

if __name__ == "__main__":

    controller = Controller()

    goal = "Create a python file that prints hello, run it, and save output"
    goal_1 = "Create a FastAPI app with one endpoint and run it"
    goal_2 = "Create a FastAPI app that is a project management system all required endpoints and run tests and tell me the result in a file named test_result.txt"
    goal_3 = """Create a Python FastAPI script withendpoints that:
- Fetches data from a public API
- Make good folder structure seperating router, service and schema
- Processes it
- Saves it to a file
- Then verifies the file content using a test
- Then run the test and tell me the result
"""
    goal_4 = """
Create a Python project that:

1. Implements a CLI tool called "file_stats.py" that:
   - Takes a file path as input
   - Reads the file
   - Calculates number of lines, words, and characters
   - Prints the result in a readable format

2. Create a sample input file with some text

3. Run the script on the sample file

4. Save the output to a file named output.txt

5. Write a pytest test that:
   - Verifies the counts are correct

6. Run the tests and ensure they pass

Constraints:
- Use simple Python (no external libraries except pytest)
- Each step must be executed using tools
- Fix any errors if they occur
- Do not assume files exist unless created"""

    controller.run(goal_4)