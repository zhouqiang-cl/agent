import subprocess

def system(cmd):
    '''
    @summary: excute a subprocess return util subprocess stopped
    @param cmd: a string that need to excute in subprocess
    @result: return_code, stdout, stderr
    '''
    process = subprocess.Popen(
        args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = process.communicate()
    return_code = process.poll()
    return return_code, std_out, std_err