import sys
from csv import reader
import copy


class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, p):
        self.queue.append(p)

    def pop(self, index):
        tmp = self.queue.pop(index)
        return tmp

    def poll(self):
        return self.queue[0]

    def empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def removeDupes(self):
        result = sorted(set(self.queue), key=self.queue.index)
        self.queue = result

    def put_in_second_last(self, value):
        if self.empty():
            self.queue.append(value)
        else:
            self.queue.insert(self.size() - 1, value)




class Pcslist:
    def __init__(self, pcs):  # pcs is a list of processes passed in as parameter to class constructor
        self.pcs = pcs
        self.ps_by_pid = sorted(pcs, key=lambda p: p.pid)
        self.ps_by_arr = sorted(pcs, key=lambda p: (p.arrt, p.pid))
        self.ps_by_burst = sorted(pcs, key=lambda p: (p.arrt, p.burstt))
        self.time = 0
        self.rrGanttList = []
        self.all_times = []

    def min(self):
        lowest = self.ps_by_arr[0]
        i = 0
        while i < len(self.ps_by_arr):
            if self.ps_by_arr[i].arrt < lowest.arrt:
                lowest = self.ps_by_arr[i]
            i += 1
        return lowest

class Process:
    def __init__(self, pid, arrt, burstt):
        self.pid = pid
        self.arrt = arrt
        self.burstt = burstt
        self.comptime = 0
        self.tatime = 0
        self.waittime = 0
        self.starttime = 0

        def __eq__(self, other):
            if isinstance(other, Process):
                return self.pid == other.pid


def waittime(ps):
    for p in ps.pcs:
        p.waittime = p.tatime - p.burstt


def tatime(ps):
    for p in ps.pcs:
        p.tatime = p.comptime - p.arrt


def printFCFS(lst):
    lst.time = 0
    print('_________________FCFS_____________________')
    print('Process ID | Waiting Time | Turnaround Time')

    i = 0
    while i < len(lst.ps_by_arr):  # TODO: add second conditional to check at i = 0 properly
        if lst.ps_by_arr[i - 1].comptime < lst.ps_by_arr[i].arrt:
            lst.time = lst.time + (lst.ps_by_arr[i].arrt - lst.ps_by_arr[i - 1].comptime)
            lst.ps_by_arr[i].starttime = lst.time
            lst.time = lst.time + lst.ps_by_arr[i].burstt
            lst.ps_by_arr[i].comptime = lst.time
        else:
            lst.ps_by_arr[i].starttime = lst.time
            lst.time = lst.time + lst.ps_by_arr[i].burstt
            lst.ps_by_arr[i].comptime = lst.time
        i += 1
    tatime(lst)
    waittime(lst)
    for p in lst.ps_by_pid:
        print(f'    {p.pid}      |      {p.waittime}       |        {p.tatime}')


def printSJF(lst, q):
    lst.time = 0
    lst.ps_by_arr = sorted(lst.pcs, key=lambda p: (p.arrt, p.pid))
    for p in lst.ps_by_burst:
        if p is not None and p.arrt <= lst.time:
            q.push(p)
            lst.ps_by_arr.remove(p)
            lst.ps_by_burst[lst.ps_by_burst.index(p)] = None

    while len(lst.ps_by_arr) > 0:

        if q.empty():  # if there is an IDLE time between processes
            lst.time = lst.ps_by_arr[0].arrt  # set time to start of next process
            q.push(lst.ps_by_arr[0])
            lst.ps_by_burst[lst.ps_by_burst.index(lst.ps_by_arr[0])] = None
            lst.ps_by_arr.remove(lst.ps_by_arr[0])

            continue
        else:
            q.queue[0].starttime = lst.time
            lst.time = lst.time + q.queue[0].burstt
            q.queue[0].comptime = lst.time
            q.pop(0)
            for p in lst.ps_by_burst:
                if p is not None and p.arrt <= lst.time:
                    q.push(p)
                    lst.ps_by_arr.remove(p)
                    lst.ps_by_burst[lst.ps_by_burst.index(p)] = None
            q.queue = sorted(q.queue, key=lambda a: a.burstt)

    q.queue[0].starttime = lst.time
    lst.time = lst.time + q.queue[0].burstt
    q.queue[0].comptime = lst.time
    q.pop(0)

    tatime(lst)
    waittime(lst)
    print('__________________SJF_____________________')
    print(' Process ID | Waiting Time | Turnaround Time')
    for p in lst.ps_by_pid:
        print(f'    {p.pid}      |      {p.waittime}       |        {p.tatime}')


def wt_for_rr(ps, cpy):
    ps.all_times = sorted(ps.all_times, key=lambda a: a.pid)
    i = 0
    while i < len(ps.all_times):
        ps.all_times[i].waittime = ps.all_times[i].tatime - cpy.ps_by_pid[i].burstt
        i += 1



def tatime_for_rr(ps):
    for p in ps.all_times:
        p.tatime = p.comptime - p.arrt


def printRR(lst, q, quantum, listcpy):
    print('_________________ Round Robin ____________________')
    print('Process ID | Waiting Time | Turnaround Time')
    lst.time = 0
    # an array for something fucking retarded (dont ask)
    dumbass = []

    # get all arrived processes and put them in a queue
    # set already used processes to null
    # sort them by PID
    for p in lst.ps_by_pid:
        if p.arrt <= lst.time:
            q.push(p)

    # ------
    # check to see if there are still elements in the temporary array to see if there are still processes to be run
    while len(lst.ps_by_arr) > 0 or q.size() > 0:
        # create temporary process to be stored later so it can be put back into the queue after new processes
        temp = None
        if q.size() != 0:
            my_var = q.pop(0)
        else:
            my_var = lst.min()
            lst.time = my_var.arrt
        testcpy = copy.deepcopy(my_var)
        # run the first one in the queue for time quantum or less
        if my_var.burstt > quantum:
            # set the start time
            my_var.starttime = lst.time
            testcpy.starttime = lst.time
            # add the time it ran for to the current time
            lst.time += quantum
            # decrease quantum from remaining burst time
            my_var.burstt -= quantum
            testcpy.burstt -= quantum
            # set the completion time
            my_var.comptime = lst.time
            testcpy.comptime = lst.time
            # add that "process" to the gant list in lst
            lst.rrGanttList.append(testcpy)
            # if it needs more time to run store it for later
            if my_var.burstt > 0:
                temp = my_var
            else:
                lst.all_times.append(lst.ps_by_pid[lst.ps_by_pid.index(my_var)])
                # if it doesn't need more time to run delete it from the temporary array
                if my_var in lst.ps_by_arr:
                    lst.ps_by_arr.remove(my_var)

            # add the previously run process to the end of the queue
            if temp is not None:
                q.push(temp)
                if temp not in dumbass:
                    dumbass.append(temp)
            # run through remaining processes and add them to the queue if they have arrived
            for p in lst.ps_by_pid:
                if p.arrt <= lst.time and p not in q.queue and p not in dumbass:
                    q.put_in_second_last(p)
                    dumbass.append(p)

        # go back to the dashes and repeat until the queue is empty
        # ------
        # if the amount of burst time is less than the quantum
        else:
            # set the start time
            my_var.starttime = lst.time
            testcpy.starttime = lst.time
            # add the time it ran for to the current time
            lst.time += my_var.burstt
            # decrease quantum from remaining burst time
            my_var.burstt = 0
            testcpy.burstt = 0
            # set the completion time
            my_var.comptime = lst.time
            testcpy.comptime = lst.time
            # add that "process" to the gant list in lst

            lst.rrGanttList.append(testcpy)

            lst.all_times.append(lst.ps_by_pid[lst.ps_by_pid.index(my_var)])
            # remove this element from the list
            if my_var in lst.ps_by_arr:
                lst.ps_by_arr.remove(my_var)

            # run through remaining processes and add them to the queue if they have arrived
            for p in lst.ps_by_pid:
                if p.arrt <= lst.time and p not in q.queue and p not in dumbass:
                    q.put_in_second_last(p)
                    dumbass.append(p)

    tatime_for_rr(lst)
    wt_for_rr(lst, listcpy)
    for v in lst.all_times:
        print(f'    {v.pid}      |       {v.waittime}      |        {v.tatime}')
    print('Gantt Chart is:')
    lst.rrGanttList = sorted(lst.rrGanttList, key=lambda a: a.starttime)
    i = 0
    while i < len(lst.rrGanttList):
        if i > 0:
            if lst.rrGanttList[i - 1].comptime < lst.rrGanttList[i].starttime:
                print(f'[  {lst.rrGanttList[i - 1].comptime}  ]--  IDLE  --[  {lst.rrGanttList[i].starttime}  ]')
        print(f'[  {lst.rrGanttList[i].starttime}  ]--  {lst.rrGanttList[i].pid}  --[  {lst.rrGanttList[i].comptime}  ]')
        i += 1

    wt = 0
    tat = 0
    for p in lst.pcs:
        wt += p.waittime
        tat += p.tatime
    wt = wt / len(lst.pcs)
    tat = tat / len(lst.pcs)
    thru = len(lst.pcs) / lst.time
    print(f'\nAverage Waiting Time: {wt: .1f}')
    print(f'Average Turnaround Time: {tat: .2f}')
    print(f'Throughput: {thru: .12f}')


def printGantt(lst):
    print('Gantt Chart is:')
    lst.ps_by_arr = sorted(lst.pcs, key=lambda a: (a.arrt, a.pid))
    i = 0
    while i < len(lst.ps_by_arr):
        if lst.ps_by_arr[i - 1].comptime < lst.ps_by_arr[i].starttime:
            print(f'[ {lst.ps_by_arr[i - 1].comptime} ]-- IDLE --[ {lst.ps_by_arr[i].starttime} ]')
        print(f'[ {lst.ps_by_arr[i].starttime}  ]-- {lst.ps_by_arr[i].pid} --[ {lst.ps_by_arr[i].comptime} ]')
        i += 1

    wt = 0
    tat = 0
    for p in lst.pcs:
        wt += p.waittime
        tat += p.tatime
    wt = wt / len(lst.pcs)
    tat = tat / len(lst.pcs)
    thru = len(lst.pcs) / lst.time
    print(f'\nAverage Waiting Time: {wt: .1f}')
    print(f'Average Turnaround Time: {tat: .2f}')
    print(f'Throughput: {thru: .12f}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Error: Found incorrect number of arguments", file=sys.stderr)
        exit(1)
    processes = []
    with open(sys.argv[1]) as f:
        rdr = reader(f, delimiter=',')
        next(rdr)
        for var in rdr:
            pid, arr_time, burst_time = var
            processes.append(Process(int(pid), int(arr_time), int(burst_time)))

    plist = Pcslist(processes)
    printFCFS(plist)
    print()
    printGantt(plist)
    print()
    queue = PriorityQueue()
    plist = Pcslist(processes)
    printSJF(plist, queue)
    printGantt(plist)
    queue = PriorityQueue()
    print()
    cpy = copy.deepcopy(plist)
    printRR(plist, queue, int(sys.argv[2]), cpy)
