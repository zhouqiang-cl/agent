from libs.misc import system
class Sys(object):
    def get_block_number(self, block):
        # "ls -lhrt"
        cmd = "ls -lhrt {block}".format(block)
        # print "start running command '{cmd}'".format(cmd=cmd)
        # "brw-rw----. 1 root disk 8, 16 Nov  6 11:57 /dev/sdb"
        rc,so,se = system(cmd)
        print rc, so, se
        return "".join(a.split()[4:6]).replace(",",":")
    def get_block_by_mount(self, mount):
        cmd = "mount"
        rc,so,se = system(cmd)
        for line in so.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.split()[2] == mount:
                return line.split()[0]

if __name__ == "__main__":
    sys = Sys()
    block = sys.get_block_by_mount("/data1")
    print block
    print sys.get_block_number(block)