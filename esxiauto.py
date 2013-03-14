#!/usr/bin/python

import sys, os, time, glob, shutil
from optparse import OptionParser
import subprocess

# -----------------------------------------------------------------------

vm_paths = {
    # the standard path on Mac OS X
    '/Library/Application Support/VMware Fusion/vmrun': 'esx',
    # the standard path on Linux
    '/usr/bin/vmrun': 'esx',
    # the standard path on Windows
    'C:\\Program Files\\VMware\\VMware Workstation\\vmrun.exe': 'esx'
    }
def pinfo(msg):
    print "[INFO] ", msg

def perror(msg):
    print "[ERROR] ", msg

# -----------------------------------------------------------------------

class VMESXiAuto:
    def __init__(self, vmx):
        self.vmx = vmx

        self.vmrun  = None
        self.vmtype = None

		#The code below ,just for personal PC, Not for ESXi or server
		#if not os.path.isfile(vmx):
        #    raise 'Cannot find vmx file in ' + vmx

        for (path,type) in vm_paths.items():
            if os.path.isfile(path):
                self.vmrun = path
                self.vmtype = type
                break

        if self.vmrun == None:
            raise 'Cannot find vmrun in ' + ','.join(vm_paths.keys())
        else:
            print 'Found vmrun (running on %s)' % self.vmtype

    def set_Hostuser(self, user, passwd):
        '''
        This is for ESXi or server,not needed for workstation
        '''
        self.host_user = user
        self.host_passwd = passwd

    def set_Guestuser(self, user, passwd):
        '''
        Sets the credentials on the guest machine to
        use when copying files to/from the guest and
        when executing programs in the guest
        '''
        self.guest_user = user
        self.guest_passwd = passwd

    def run_cmd(self, cmd, args=[], guest=False):
        '''
        Execute a command through vmrun. Additional
        parameters for commands can be set with args[]
        '''
        print 'Executing ' + cmd + ' please wait...'
        pargs = [self.vmrun, '-T', self.vmtype,'-u',self.host_user,'-p',self.host_passwd]
        if guest:
            pargs.extend(['-gu', self.user])
            pargs.extend(['-gp', self.passwd])
        pargs.append(cmd)
        pargs.append(self.vmx)
        pargs.extend(args)

        proc = subprocess.Popen(
            pargs,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return proc.communicate()[0]

    def list(self):
        '''
        List the running virtual machines
        '''
        pargs = [self.vmrun, 'list']
        print pargs
        proc = subprocess.Popen(
            pargs,
            stdout=subprocess.PIPE
        )
        return proc.communicate()[0]

    def start(self):
        '''
        Start the virtual machine specified by self.vmx
        '''
        return self.run_cmd('start')

    def stop(self):
        '''
        Stop the virtual machine specified by self.vmx
        '''
        return self.run_cmd('stop')

    def revert(self, snapname):
        '''
        Revert the virtual machine specified by self.vmx
        to the given snapshot
        '''
        return self.run_cmd('revertToSnapshot', [snapname])

    def suspend(self):
        '''
        Suspend the virtual machine specified by self.vmx.
        This is usually done after executing malware in order
        freeze the machine's state and obtain its physical
        memory sample
        '''
        return self.run_cmd('suspend')

    def scrshot(self, outfile):
        '''
        Take a screen shot of the guest's desktop and
        save it to the file specified by outfile
        '''
        return self.run_cmd('captureScreen', [outfile], guest=True)

    def copytovm(self, src, dst):
        '''
        Copy the src file (src is a path on the host) to
        dst (dst is a path on the guest).
        '''
        if not os.path.isfile(src):
            perror('Cannot locate source file ' + src)
            return
        return self.run_cmd(
            'copyFileFromHostToGuest', [src, dst], guest=True)

    def copytohost(self, src, dst):
        '''
        Copy the src file (src is a path on the guest) to
        dst (dst is a path on the host).
        '''
        return self.run_cmd(
            'copyFileFromGuestToHost', [src, dst], guest=True)

    def winexec(self, file, args=''):
        '''
        Execute a command in the guest with supplied arguments.
        You can use this to execute malware or existing programs
        on the guest machine such as monitoring tools or whatever.
        '''
        return self.run_cmd(
            'runProgramInGuest',
            [
                '-noWait',
                '-interactive',
                '-activeWindow',
                file, args
            ],
            guest=True)

    def findmem(self):
        '''
        Find the file on the host machine's file system that
        represents the guest's physical memory. This is usually
        only available when the guest is suspended
        '''
        path = os.path.dirname(self.vmx)
        mems = glob.glob('%s/*.vmem' % (path))
        mems = [m for m in mems if "Snapshot" not in m]
        return mems[0] if len(mems) else ''

def main(argv):
    print 'Nothing to do. Import me!'
    return 0

if __name__ == '__main__':
    main(sys.argv)
