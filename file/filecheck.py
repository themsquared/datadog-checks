import time
import os

from checks import AgentCheck

class FileCheck(AgentCheck):
    def check(self, instance):
        if 'path' not in instance:
            self.log.info("Skipping instance, no path found.")
            return

        path = instance['path']
        result = AgentCheck.CRITICAL
        message = "File "+path+" was not found.";
        if os.path.isfile(path):
            result = AgentCheck.OK
            message = "File "+path+" was found."
            
            st=os.stat(path)    
            mtime=st.st_mtime
            age=time.time()-mtime
            self.gauge('file.modified',mtime,["path"+path])
            self.gauge('file.age',age,["path"+path])
        
        self.service_check('file.exists',result,tags=["path"+path],message=message)

if __name__ == '__main__':
    print "..."
