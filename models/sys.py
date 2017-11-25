class Sys(object):
    def get_block_number(self, block):
        "ls -lhrt"
        cmd = "ls -lhrt {block}".format(block)
        # print "start running command '{cmd}'".format(cmd=cmd)
        "brw-rw----. 1 root disk 8, 16 Nov  6 11:57 /dev/sdb"
        rc,so,se = system(cmd)
        print rc, so, se
        return "".join(a.split()[4:6]).replace(",",":")