import subprocess

# if the script don't need output.
subprocess.call("php C:/xampp/htdocs/sephp/d.php")

# if you want output
proc = subprocess.Popen("php C:/xampp/htdocs/sephp/d.php", shell=True, stdout=subprocess.PIPE)
print (proc)
script_response = proc.stdout.read()