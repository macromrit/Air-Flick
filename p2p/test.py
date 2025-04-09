import subprocess

result = subprocess.run(['python', 'subscriber.py'], capture_output=True, text=True)

output = result.stdout.strip()  # Clean the output
print("Output from other_file.py:", output)
