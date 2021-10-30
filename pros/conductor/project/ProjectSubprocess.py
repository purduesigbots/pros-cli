import subprocess
import sys
from pros.common.utils import logger
class Subprocess:
    def __init__(self,exe,arg,c,e):
        self.ex=exe
        self.arg=arg
        self.c=c
        self.e=e
        self.process,self.stdout_pipe,self.stderr_pipe = (None,None,None)
        self.start()

    def start(self):
        try:
            self.process = subprocess.Popen(executable=self.ex,args=self.arg,cwd=self.c,env=self.e,
                                            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.stdout_pipe,self.stderr_pipe=self.process.communicate()
            self.process.wait()
            self.close_pipes()
        except Exception as e:
            self.error_handle(e)

    def error_handle(self,e):
        if type(e)==FileNotFoundError:
            logger(__name__).error("\nUnable to locate executable \'" + self.ex + ".exe\'! Are you sure PROS was installed correctly?\n"+str(e))
        else:
            logger(__name__).error(e)
        sys.exit()

    def close_pipes(self):
        self.stdout_pipe.close()
        self.stderr_pipe.close()
