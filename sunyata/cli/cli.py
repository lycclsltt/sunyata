import argparse
import sys
import os
from sunyata.rpc.server import TcpRpcServer

class Cli(object):

    def entryPoint(self):
        args = self.parseArgs()
        self.runServer(args)

    def parseArgs(self):
        parser = argparse.ArgumentParser(description="sunyata console cli tool")
        parser.add_argument('-r', '--run', type=str, help = 'module', required=True, metavar='module', dest='module')
        parser.add_argument('-b', '--bind', type=str, help='bind interface, default 0.0.0.0', default='0.0.0.0', required=False, metavar='0.0.0.0', dest='bind')
        parser.add_argument('-p', '--port', type=int, help='bind port, default 9988', default=9988, required=False, metavar='9988', dest='port')
        args = parser.parse_args()
        try:
            module = args.module
            if module == '':
                raise Exception('')
        except Exception as ex:
            print(ex)
            parser.print_usage()
            sys.exit(1)
        return args

    def runServer(self, args):
        sys.path.append( os.getcwd() )
        __import__(args.module)
        s = TcpRpcServer(args.bind, args.port)
        s.serve()