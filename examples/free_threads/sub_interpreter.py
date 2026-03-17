import threading

import _interpreters

# 1. Create a new, isolated subinterpreter
interp_id = _interpreters.create()

# 2. Define the code to run (must be a string for the low-level API)
# This code sets a variable that only exists inside the subinterpreter.
code = """
import os
val = "Hello from Subinterpreter!"
print(f"Subinterpreter says: {val} (PID: {os.getpid()})")
"""


# 3. Run the code inside the subinterpreter
# We use a thread so it can run concurrently with our main code
def run_worker():
    _interpreters.run_string(interp_id, code)


thread = threading.Thread(target=run_worker)
thread.start()
thread.join()

# 4. Cleanup
_interpreters.destroy(interp_id)

print("Main interpreter: Work complete.")
