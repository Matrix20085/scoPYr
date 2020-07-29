import os
import re
import math
import argparse
import ipaddress

from pathlib import Path
from collections import deque


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', action='store', dest='inputFileVar', required=True, help='Path to input file')
parser.add_argument('-e', '--exclude', action='store', dest='excludeFileVar', help='Path to exclude file')
parser.add_argument('-o', '--output', action='store', dest='outputFileVar', default=os.getcwd() + "/output.txt", help='Output file')
parser.add_argument('-s', '--split', action='store', dest='splitCount', type=int, default=1, help='Number of files to split results into')
args = parser.parse_args()

args.outputFileVar = Path(args.outputFileVar)

regexPatterns = {}
regexPatterns['cidr'] = r'^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$'
regexPatterns['lastOctet'] = r'^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$'
regexPatterns['allOctets'] = r'^(\d{1,3}\.){3}(\d{1,3})-(\d{1,3}\.){3}\d{1,3}$'
regexPatterns['single'] = r'^(\d{1,3}\.){3}(\d{1,3})$'


outputFile = open(args.outputFileVar, 'a')
inputFile = open(args.inputFileVar, 'r')
if args.excludeFileVar: excludeFile = open(args.excludeFileVar, 'r')


def expand(ipRange):
    scope = []
    if re.search(regexPatterns['cidr'], ipRange):
        net = ipaddress.ip_network(ipRange)
        for adder in net:
            scope.append(str(ipaddress.IPv4Address(adder)))
    elif re.search(regexPatterns['lastOctet'], ipRange):
        adder = ipRange.split('.')
        startEnd = adder[3].split('-')
        start = int(startEnd[0])
        end = int(startEnd[1])
        for i in range(start, end + 1):
            scope.append(adder[0] + '.' + adder[1] + '.' + adder[2] + '.' + str(i))
    elif re.search(regexPatterns['allOctets'], ipRange):
        startEnd = ipRange.split('-')
        start_ip = ipaddress.IPv4Address(startEnd[0])
        end_ip = ipaddress.IPv4Address(startEnd[1])
        for ip_int in range(int(start_ip), int(end_ip) + 1):
            scope.append(str(ipaddress.IPv4Address(ip_int)))
    elif re.search(regexPatterns['single'], ipRange):
        scope.append(ipRange)
    else:
        print("Can not parse: " + ipRange)
        return []
    return scope


excludeList = []
try:
    if excludeFile:
        excludeList = []
        for case in excludeFile:
            case = case.rstrip("\n")
            for i in expand(case):
                excludeList.append(i)

        excludeFile.close()
except:
    print("Not using an exclude file")


for case in inputFile:
    case = case.rstrip("\n")
    for i in expand(case):
        if i not in excludeList:
           print(i, file=outputFile)
    

outputFile.close()
inputFile.close()


if args.splitCount > 1:
    allIps = deque([])
    with open(args.outputFileVar, 'r') as fullList:
        for line in fullList:
            allIps.append(line)
    numPerFile = math.ceil(len(allIps)/args.splitCount)
    print(len(allIps))
    print(numPerFile)
    for fileNum in range(0,args.splitCount):
        with open(Path(str(args.outputFileVar) + str(fileNum)), 'a') as outputFile:
            for count in range(0,numPerFile):
                if len(allIps) > 0: print(allIps.popleft().rstrip("\n"), file=outputFile)
                else: break