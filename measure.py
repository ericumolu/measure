#!/usr/local/lib/python3.3

#    This file is part of measure.
#
#    measure is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    measure is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with measure.  If not, see <http://www.gnu.org/licenses/>.

from time import time

class TimedRun:
    def __init__(self):            
        self.start()
        self.stopped = 0
        self.run_id = ""

    def start(self):
        self.start_time = time()
        return self.start_time

    def stop(self):
        if not self.stopped:
            self.stop_time = time()
            self.stopped = 1
        return self.stop_time
    
    def total(self):
        if not self.stopped:
            self.stop()
        self.total_time = self.stop_time - self.start_time
        return self.total_time

    def id(self,id=""):
        if id:
            self.run_id = id
        else:
            return self.run_id

class TimedBlock:
    def __init__(self,id):
        self.timed_run = []
        self.id = id

    def add_timed(self):
        self.timed_run.append(TimedRun())

    def get_times(self,index=None):
        times = []

        if index is None:
            for time in self.timed_run:
                times.append(time.total())
        else:
            times = self.timed_run[index]
        return times    

    def total_timed(self):
        total = 0
        for time in self.timed_run:
            total += time.total()
        return total

    def stop_timed(self):
        for time in self.timed_run:
            time.stop()

    def average(self):
        total = 0
        for time in self.timed_run:
            total += time.total()
        return total / len(self.timed_run)

    def use_percent(self,time):
        return (time / self.total_timed()) * 100
    
    def xml_child_number(self,number=None):
        if number is None:
            return self.xml_child
        else:
            self.xml_child = number

class TreeNode:
    def __init__(self, id="", parent=None):
        self.parent = parent
        self.tree_node = []
        self.id = id

    def add_id(self, id):
        self.tree_node.append(TreeNode(id,self.parent))
        self.tree_node[-1].parent = self

    def get_id(self,id):
        #use this method over get_id_node because get_id_node wont clear match list,do here instead
        match = []
        self.get_id_node(id,match)
        return match

    def get_id_node(self,id,match):
        if id == self.id:
            match.append(self)
            
        for node in self.tree_node:
            node.get_id_node(id,match)

        return match

class BlockTree:
    def __init__(self):
        self.tree = TreeNode()
        self.current_node = self.tree

    def add(self,block):
        self.current_node.add_id(block)
        child_number = self.xml_child_count = len(self.current_node.tree_node) - 1
        self.current_node = self.current_node.tree_node[-1]
        return child_number

    def current_to_block(self,child_number):
        self.current_node = self.current_node.tree_node[child_number]
    
    def close(self,block):
        self.current_node = self.current_node.parent

class Measure:
    def __init__(self):
        self.id_label = 'id'
        self.block = {}
        self.block[self.id_label] = {}
        self.block_map = BlockTree()
        self.last_block = []
        self.top_block = "main"
        self.header_format = "\n{id:<20}{run_count:<10}{time:<30}{of_parent:<30}{of_total:<30}"
        self.time_format = "\n{id:<20}{run_count:<10}{time:<30}{of_parent:<30.4}{of_total:<30.4}"
        self.line_lenght = 110
        self.gap = 10

    def set_sub(self):
        child_number = self.block[self.id_label][self.last_block[-1]].xml_child_number()
        self.block_map.current_to_block(child_number)

    def add_sub(self):
        child_number = self.block_map.add(self.last_block[-1])
        self.block[self.id_label][self.last_block[-1]].xml_child_number(child_number)

    def close_sub(self):
        self.block_map.close(self.last_block[-1])

    def add_block(self,id,group=[]):
        #reset the object state at start,becasue measure.msr can be used as a global and retain its current state after each run on a wsgi application
        if id == self.top_block:
            self.__init__()

        self.last_block.append(id)

        if self.last_block[-1] in self.block[self.id_label]:
            self.set_sub()
        else:
            self.block[self.id_label][self.last_block[-1]] = TimedBlock(self.last_block[-1])
            self.block_count()
            self.add_sub()

        self.block[self.id_label][self.last_block[-1]].add_timed()
        if len(group):
            self.add_group(group)
    
    def block_count(self):
        self.block[self.id_label][self.last_block[-1]].b_count = len(self.block[self.id_label]) - 1

    def add_group_ver1(self,group,last=None):
        if len(group) < 1:
            last[self.id_label] = {}
            last[self.id_label][self.last_block[-1]] = self.block[self.id_label][self.last_block[-1]]
            return 0

        if last == None:
            last = self.block

        last[group[0]] = {}
        last = last[group[0]]
        self.add_group(group[1:],last)  

    #add_group_ver2
    def add_group(self,group):
        last = self.block

        for count in range(len(group)):
            if group[count] not in last:
                last[group[count]] = {}
            last = last[group[count]]

        if self.id_label not in last:
            last[self.id_label] = {}

        last[self.id_label][self.last_block[-1]] = self.block[self.id_label][self.last_block[-1]]
        return 1

    def report_group(self,group):
        last = self.block

        for count in range(len(group)):
            last = last[group[count]]

        last = last[self.id_label]
        return self.report(last)

    #stop all times within a block
    def stop_block(self,block=""):
        self.close_sub()

        if block:
            if block in self.block[self.id_label]:
                self.block[self.id_label][block].stop_timed()
        else:
            self.block[self.id_label][self.last_block.pop()].stop_timed()

    def report(self,select=[]):
        self.show = "\n" * self.gap

        if not select:
            select = self.block[self.id_label]
        self.show += self.header_format.format(id="Id",run_count="Run",time="Time (sec)",of_parent="% of Parent",of_total="% of Total")

        for block in self.sort_block(select):
            self.show +="\n\n" + block
            self.show += "\n{line}".format(line="-"*self.line_lenght) 

            count = 0
            parent = self.block_map.tree.get_id(block)[0].parent.id

            for run in self.block[self.id_label][block].timed_run:
                if block == self.top_block:
                    of_parent = 100.0
                else:
                    of_parent = self.block[self.id_label][parent].use_percent(run.total())
                of_total = self.block[self.id_label][self.top_block].use_percent(run.total())
                id = run.id()
                self.show += self.time_format.format(id=id,run_count=str(count),time=str(run.total()),of_parent=of_parent,of_total=of_total)
                count += 1
                    
            if count > 1:
                self.add_total(block,parent)
                self.add_average(block,parent)              

        return self.show

    def sort_block(self,block_list,rev=False):
        return sorted(block_list,key=lambda block: self.block[self.id_label][block].b_count,reverse=rev)

    def add_total(self,block,parent):
        block_total = self.block[self.id_label][block].total_timed()
        of_parent = self.block[self.id_label][parent].use_percent(block_total)
        of_total = self.block[self.id_label][self.top_block].use_percent(block_total)
        self.show += self.time_format.format(id="",run_count="total",time=str(block_total),of_parent=of_parent,of_total=of_total)       

    def add_average(self,block,parent):
        block_ave = self.block[self.id_label][block].average()
        of_parent = self.block[self.id_label][parent].use_percent(block_ave)
        of_total = self.block[self.id_label][self.top_block].use_percent(block_ave)
        self.show += self.time_format.format(id="",run_count="ave",time=str(block_ave),of_parent=of_parent,of_total=of_total)

#use globe if you want to report over multiple modules
globe = Measure()
