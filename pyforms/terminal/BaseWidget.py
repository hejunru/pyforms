from pyforms.Controls import ControlFile, ControlSlider, ControlText, ControlCombo, ControlCheckBox
from datetime import datetime, timedelta
import argparse, uuid, os, shutil, time, sys, subprocess

try:
    import requests
except:
    print "No requests lib"


class BaseWidget(object):

    _parser = argparse.ArgumentParser()

    def __init__(self, title):
        f = open('pid.txt', 'w')
        f.write(str(os.getpid()))
        f.close()
        
        self._title = title
        self.stop = False

    ############################################################################
    ############ Module functions  #############################################
    ############################################################################

    def initForm(self):
        result = {}
        for name, var in vars(self).items():
            if isinstance(var, (ControlFile,ControlSlider,ControlText, ControlCombo,ControlCheckBox) ):
                self._parser.add_argument("--%s" % name, help=var.label)
        
        args = self._parser.parse_args()
        for name, var in vars(self).items():
            if name not in args.__dict__: continue

            if isinstance(var, ControlFile):
                value = args.__dict__[name]
                if value!=None and (value.startswith('http://') or value.startswith('https://')):
                    local_filename = value.split('/')[-1]
                    outputFileName = os.path.join('input', local_filename)
                    self.__downloadFile(value, outputFileName)
                    var.value = outputFileName
                else:
                    var.value = value

            elif isinstance(var,  (ControlText, ControlCombo)):
                var.value = args.__dict__[name]
            elif isinstance(var, ControlCheckBox):
                var.value = args.__dict__[name]=='True'
            elif isinstance(var, ControlSlider):
                var.value = int(args.__dict__[name])

        self.execute()


    def __downloadFile(self, url, outFilepath):
        chunksize = 512*1024
        r = requests.get(url, stream=True)
        with open(outFilepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunksize): 
                if chunk: f.write(chunk); f.flush(); 
        


    def execute(self): pass


    def start_progress(self, total = 100):
        self._total_processing_count = total
        self._processing_initial_time = time.time()
        self._processing_count  = 1

    def update_progress(self):
        div = int(self._total_processing_count/400)
        if div==0: div = 1
        if (self._processing_count % div )==0:
            self._processing_last_time = time.time()  
            total_passed_time = self._processing_last_time - self._processing_initial_time
            remaining_time = ( (self._total_processing_count * total_passed_time) / self._processing_count ) - total_passed_time
            if remaining_time<0: remaining_time = 0
            time_remaining = datetime(1,1,1) + timedelta(seconds=remaining_time )
            time_elapsed = datetime(1,1,1) + timedelta(seconds=(total_passed_time) )

            values = ( 
                        time_elapsed.day-1,  time_elapsed.hour, time_elapsed.minute, time_elapsed.second, 
                        time_remaining.day-1, time_remaining.hour, time_remaining.minute, time_remaining.second, 
                        (float(self._processing_count)/float(self._total_processing_count))*100.0, self._processing_count, self._total_processing_count, 
                    )

            print "Elapsed: %d:%d:%d:%d; Remaining: %d:%d:%d:%d; Processed %0.2f %%  (%d/%d); |   \r" % values, 
            sys.stdout.flush()

        self._processing_count  += 1

    def end_progress(self):
        self._processing_count = self._total_processing_count
        self.update_progress()



    def __savePID(self, pid):
        try:
            with open('pending_PID.txt', 'w') as f:
                f.write(str(pid))
                f.write('\n')
        except (IOError) as e:
            raise e

    def __savePID(self, pid):
        try:
            with open('pending_PID.txt', 'w') as f:
                f.write(str(pid))
                f.write('\n')
        except (IOError) as e:
            raise e

    def executeCommand(self, cmd, cwd=None):
        if cwd!=None: 
            currentdirectory = os.getcwd()
            os.chdir(cwd)
        
        print " ".join(cmd)
        proc = subprocess.Popen(cmd)

        if cwd!=None: os.chdir(currentdirectory)
        self.__savePID(proc.pid)
        proc.wait()
        #(output, error) = proc.communicate()
        #if error: print 'error: ', error
        #print 'output: ', output
        return ''#output
