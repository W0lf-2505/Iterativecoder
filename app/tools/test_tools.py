# Our Agent Runs tests on the code it generates. This file contains the tools for running those tests.

def run_tests(test_cases):
    results = []
    for test in test_cases:
        try:
            exec(test['code'])
            results.append({'test': test['name'], 'result': 'Passed'})
        except Exception as e:
            results.append({'test': test['name'], 'result': f'Failed: {str(e)}'})
    return results