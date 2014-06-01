import sys
import struct
f1 = open('bash_result.txt', 'a')
sys.stdout = f1
print '1'
print '2'
print '3'
f1.close()
