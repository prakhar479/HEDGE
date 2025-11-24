import subprocess
import sys
import os
import json
import tempfile
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class CodeRunner:
    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def run(self, code_str: str, test_code_str: str) -> Tuple[bool, Dict[str, float], str]:
        """
        Runs the provided code string against the test code string.
        Returns:
            success: bool (True if tests passed)
            metrics: dict (energy, time, etc.)
            output: str (stdout/stderr)
        """
        
        # Create a temporary directory for this run
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write the candidate code
            candidate_path = os.path.join(tmpdir, "candidate.py")
            with open(candidate_path, "w") as f:
                f.write(code_str)
            
            # Write the harness script
            harness_code = f"""
import sys
import os
import json
import traceback
import time

# Add current dir to path so we can import candidate
sys.path.append('{tmpdir}')

# Add project root to path so we can import src
sys.path.append('{os.getcwd()}')

try:
    from src.green_gym.monitor import EnergyMonitor
except ImportError:
    print("Error: Could not import EnergyMonitor. Check PYTHONPATH.", file=sys.stderr)
    sys.exit(1)

import candidate

{test_code_str}

if __name__ == "__main__":
    monitor = EnergyMonitor()
    monitor.start()
    
    success = False
    try:
        # Check if 'test' function exists
        if 'test' in globals():
            globals()['test']()
            success = True
        else:
            # If no test function, we assume the script body was the test
            # and if we reached here, it didn't crash.
            success = True
            
    except Exception:
        traceback.print_exc()
        success = False
        
    metrics = monitor.stop()
    
    result = {{
        "success": success,
        "metrics": metrics
    }}
    
    print("__HEDGE_RESULT_START__")
    print(json.dumps(result))
    print("__HEDGE_RESULT_END__")
"""
            harness_path = os.path.join(tmpdir, "harness.py")
            with open(harness_path, "w") as f:
                f.write(harness_code)

            # Run the harness
            cmd = [sys.executable, harness_path]
            
            try:
                # We need to set PYTHONPATH to include the project root so it can find src.green_gym
                env = os.environ.copy()
                env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    env=env,
                    cwd=tmpdir # Run inside tmpdir
                )
                
                stdout = process.stdout
                stderr = process.stderr
                
                if process.returncode != 0:
                    # If it failed, check if we got a result anyway (e.g. assertion error caught in harness)
                    if "__HEDGE_RESULT_START__" in stdout:
                        pass # We can parse it below
                    else:
                        logger.warning(f"Process failed with return code {process.returncode}")
                        return False, {}, stdout + "\n" + stderr

                # Parse the output for the JSON result
                if "__HEDGE_RESULT_START__" in stdout:
                    try:
                        json_str = stdout.split("__HEDGE_RESULT_START__")[1].split("__HEDGE_RESULT_END__")[0]
                        result = json.loads(json_str)
                        return result["success"], result["metrics"], stdout
                    except Exception as e:
                        return False, {}, f"Failed to parse result JSON: {e}\nOutput:\n{stdout}"
                else:
                    return False, {}, "Could not find result in output.\n" + stdout + "\n" + stderr

            except subprocess.TimeoutExpired:
                return False, {"timeout": True}, "Timeout expired"
            except Exception as e:
                return False, {}, str(e)
