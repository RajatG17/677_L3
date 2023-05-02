import subprocess
import os
import signal

#output = subprocess.check_output("sudo lsof -t -i:6000", shell=True)
#output = str(output.decode("utf-8"))
#output = output.split('\\n')
#res = int(output[0])
#print(res)

#os.kill(res, signal.SIGTERM)

#env = os.environ

#myvar = {'CATALOG_PORT': "6000"}

#env.update(myvar)

os.system("sudo kill -9 $(sudo lsof -t -i:6000)")
#os.system("CATALOG_PORT=6000 python3 ../catalog/catalogService.py &")

subprocess.Popen(["python3", "../catalog/catalogService.py"], close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#subprocess.run ( [ "python3", "../catalog/catalogService.py"] , text=True, env=env)
