__author__ = 'jheka'

# -*- coding: utf-8 -*-
import sys
import codecs

utf8stdout = open(1, 'w', encoding='utf-8', closefd=False) # fd 1 is stdout
print('ghgh Кот', file=utf8stdout)

# print(sys.stdout.encoding)
# print("Кот dd".encode(sys.stdout.encoding, errors='replace').decode('utf-8'))

# print("dfdf Тут")
#
# if sys.stdout.encoding != 'cp850':
#   sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'strict')
# if sys.stderr.encoding != 'cp850':
#   sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'strict')


