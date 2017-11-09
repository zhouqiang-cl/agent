#!/usr/bin/env python
import copy

class Arg(object):
    @staticmethod
    def replace_argument(cmd, agrument, replacer):
        cmd = cmd.split()
        if agrument in cmd:
            cmd[cmd.index(agrument) + 1] = replacer
        else:
            ret = copy.copy(cmd[0:-1])
            ret.extend([agrument, replacer, cmd[-1]])
            cmd = " ".join(cmd)
        return cmd

arg = Arg()
if __name__ == "__main__":
    arg = Arg()
    print arg.replace_argument("disk -i 100 -t 40 start","-t", 200)
