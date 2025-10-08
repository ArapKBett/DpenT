import asyncio
import subprocess
import sys

async def run_all_tests():
    tests = [
        "permission_analyzer.py",
        "role_escalation.py", 
        "webhook_exploit.py",
        "channel_permission_test.py"
    ]
    
    for test in tests:
        print(f"\n{'='*50}")
        print(f"Running {test}...")
        print('='*50)
        
        result = subprocess.run([sys.executable, test], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("ERRORS:", result.stderr)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
