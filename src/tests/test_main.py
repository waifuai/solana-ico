import subprocess

def test_main_invocation():
    result = subprocess.run(["python", "main.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0