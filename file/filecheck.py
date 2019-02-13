import time
import os

from checks import AgentCheck

files = {}
first_run = True

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

            if first_run:
                files[path] = mtime
                first_run = False
            else
                if mtime != files[path]:
                    self.service_check('file.exists',AgentCheck.OK,tags=["path"+path],message=message)
                else:
                    self.service_check('file.exists',AgentCheck.CRITICAL,tags=["path"+path],message=message)

            self.gauge('file.modified',mtime,["path"+path])
            self.gauge('file.age',age,["path"+path])
        
        self.service_check('file.exists',result,tags=["path"+path],message=message)

if __name__ == '__main__':
    check, instances = HTTPCheck.from_yaml('/etc/datadog-agent/conf.d/http.yaml')
    for instance in instances:
        print "\nRunning the check against url: %s" % (instance['url'])
        check.check(instance)
        if check.has_events():
            print 'Events: %s' % (check.get_events())
        print 'Metrics: %s' % (check.get_metrics())
