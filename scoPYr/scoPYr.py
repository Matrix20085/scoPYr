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


outputFile = open(args.outputFileVar, 'a')
inputFile = open(args.inputFileVar, 'r')
if args.outputFileVar: excludeFile = open(args.outputFileVar, 'r')


for case in inputFile:
    case = case.rstrip("\n")
    if re.search(regexPatterns['cidr'], case):
        print("CIDR: " + case)
        net = ipaddress.ip_network(case)
        for adder in net:
            print(adder, file=outputFile)
    elif re.search(regexPatterns['lastOctet'], case):
        print("lastOctet: " + case)
        adder = case.split('.')
        startEnd = adder[3].split('-')
        for i in range(int(startEnd[0]), int(startEnd[1]) + 1):
            print(adder[0] + '.' + adder[1] + '.' + adder[2] + '.' + str(i), file=outputFile)
    elif re.search(regexPatterns['allOctets'], case):
        startEnd = case.split('-')
        start_ip = ipaddress.IPv4Address(startEnd[0])
        end_ip = ipaddress.IPv4Address(startEnd[1])
        for ip_int in range(int(start_ip), int(end_ip) + 1):
            print(ipaddress.IPv4Address(ip_int), file=outputFile)
    else:
        print("Unmatched: " + case)

outputFile.close()
inputFile.close()
if excludeFile: excludeFile.close()

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