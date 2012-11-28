#!/usr/local/bin/python3.3

import os
from measure import globe


globe.add_block("main")

globe.add_block("sub1",['group1'])

globe.add_block("sub2")
for i in range(9999):i
globe.stop_block()

globe.stop_block()

globe.add_block("sub3",['group1'])

globe.add_block("sub4")
for i in range(9999):i
globe.stop_block()

globe.add_block("sub5")
for c in range(999920):c
globe.stop_block()

globe.stop_block()

globe.stop_block()


print (globe.report())

print (globe.report_group(['group1']))

