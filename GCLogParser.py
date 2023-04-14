import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys

class GCLogParser:
    pauseYoung_pattern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc\s*\] GC\((\d+)\) Pause Young \(([^)]+)\) \(([^)]+)\) (\d+)M->(\d+)M\((\d+)M\) (\d+\.\d+)ms$"
    pauseFull_pattern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc\s*\] GC\((\d+)\) Pause Full \(([^)]+)\) (\d+)M->(\d+)M\((\d+)M\) (\d+\.\d+)ms$"
    concurrentCycle_patttern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc\s*\] GC\((\d+)\) (Concurrent Cycle|Pause Remark|Pause Cleanup)( (\d+)M->(\d+)M\((\d+)M\))?( (\d+\.\d+)ms)?$"
    concurrentMarking_pattern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc\,marking\s*\] GC\((\d+)\) Concurrent (Clear Claimed Marks|Scan Root Regions|Mark From Roots|Preclean|Mark|Rebuild Remembered Sets|Cleanup for Next Mark)( \(\d+\.\d+s\, \d+\.\d+s\))? (\d+\.\d+)ms$"
    heap_pattern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc,heap\s*\] GC\((\d+)\) (Eden regions|Survivor regions|Old regions|Humongous regions): (\d+)->(\d+)(\((\d+)\))?$"

    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.content = file.read()
            self.lines = self.content.split("\n")
        self.cycles = [0] * len(self.lines)
        self.__build()
        self.cycles = list(filter(lambda x: x != 0, self.cycles))

    def __build(self):
        self.parse_pauseYoung()
        self.parse_conccurentCycle()
        self.parse_pauseFull()

    def parse_pauseYoung(self):
        for log in self.lines:
            match = re.search(self.pauseYoung_pattern, log)
            if match:
                # Extract the captured groups from the match object
                time_elapsed = float(match.group(1))
                gc_cycle = int(match.group(2))
                gc_type = match.group(3)
                pause_reason = match.group(4)
                before = int(match.group(5))
                after = int(match.group(6))
                total = int(match.group(7))
                duration = float(match.group(8))

                self.cycles[gc_cycle] = pauseYoung(time_elapsed, gc_cycle, gc_type, pause_reason, before, after, total, duration)

    def parse_conccurentCycle(self):
        for log in self.lines:
            match = re.search(self.concurrentCycle_patttern, log)
            if match:
                # Extract the captured groups from the match object
                time_elapsed = float(match.group(1))
                gc_cycle = int(match.group(2))
                event = match.group(3)
                heap_memory = match.group(4)
                before = match.group(5)
                after = match.group(6)
                total = match.group(7)
                duration = match.group(9)

                if event == "Concurrent Cycle":
                    if duration is not None:
                        self.cycles[gc_cycle].duration = self.cycles[gc_cycle].concurrentCycle.duration
                        self.cycles[gc_cycle].concurrentCycle.time_elapsed_end = time_elapsed
                        self.cycles[gc_cycle].time_elapsed = time_elapsed
                        continue
                    self.cycles[gc_cycle] = concurrentCycles(concurrentCycle(), pauseRemarkCleanup(), pauseRemarkCleanup())
                    self.cycles[gc_cycle].concurrentCycle.gc_cycle = gc_cycle
                    self.cycles[gc_cycle].gc_cycle = gc_cycle
                    self.cycles[gc_cycle].concurrentCycle.event = event
                    self.cycles[gc_cycle].concurrentCycle.time_elapsed_start = time_elapsed
                    continue
                elif event == "Pause Remark":
                    self.cycles[gc_cycle].pauseRemark.time_elapsed = time_elapsed
                    self.cycles[gc_cycle].pauseRemark.gc_cycle = gc_cycle
                    self.cycles[gc_cycle].pauseRemark.event = event
                    self.cycles[gc_cycle].pauseRemark.heap_memory = heap_memory
                    self.cycles[gc_cycle].pauseRemark.before = before
                    self.cycles[gc_cycle].pauseRemark.after = after
                    self.cycles[gc_cycle].pauseRemark.total = total
                    self.cycles[gc_cycle].pauseRemark.duration = duration
                    self.cycles[gc_cycle].pauseRemark.diff = int(before) - int(after)
                    continue
                elif event == "Pause Cleanup":
                    self.cycles[gc_cycle].pauseCleanup.time_elapsed = time_elapsed
                    self.cycles[gc_cycle].pauseCleanup.gc_cycle = gc_cycle
                    self.cycles[gc_cycle].pauseCleanup.event = event
                    self.cycles[gc_cycle].pauseCleanup.heap_memory = heap_memory
                    self.cycles[gc_cycle].pauseCleanup.before = before
                    self.cycles[gc_cycle].pauseCleanup.after = after
                    self.cycles[gc_cycle].pauseCleanup.total = total
                    self.cycles[gc_cycle].pauseCleanup.duration = duration
                    self.cycles[gc_cycle].pauseCleanup.diff = int(before) - int(after)
                    continue

            match = re.search(self.concurrentMarking_pattern, log)
            if match:
                time_elapsed = float(match.group(1))
                gc_cycle = int(match.group(2))
                event = match.group(3)
                duration = match.group(5)

                self.cycles[gc_cycle].concurrentCycle.duration += float(duration)
                continue

    def parse_pauseFull(self):
        for log in self.lines:
            match = re.search(self.pauseFull_pattern, log)
            if match:
                # Extract the captured groups from the match object
                time_elapsed = float(match.group(1))
                gc_cycle = int(match.group(2))
                pause_reason = match.group(3)
                before = int(match.group(4))
                after = int(match.group(5))
                total = int(match.group(6))
                duration = float(match.group(7))

                self.cycles[gc_cycle] = pauseFull(time_elapsed, gc_cycle, pause_reason, before, after, total, duration)

    def cycle(self, gc_cycle):
        return self.cycles[gc_cycle]

    def mstos(self, ms):
        # in s
        return ms / 1000

    def totalTime(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            total += cycle.duration
        return float("{:.3f}".format(total))
    
    def totalTimeConcurrentCycle(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            if isinstance(cycle, concurrentCycles):
                total += cycle.duration
        return float("{:.3f}".format(total))
    
    def totalTimePauseTime(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            if isinstance(cycle, pauseYoung) or isinstance(cycle, pauseFull):
                total += cycle.duration
            elif isinstance(cycle, concurrentCycles):
                total += float(cycle.pauseRemark.duration)
                total += float(cycle.pauseCleanup.duration)
        return float("{:.3f}".format(total))
    
    def totalTimePauseYoung(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            if isinstance(cycle, pauseYoung):
                total += cycle.duration
        return float("{:.3f}".format(total))
    
    def totalTimePauseFull(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            if isinstance(cycle, pauseFull):
                total += cycle.duration
        return float("{:.3f}".format(total))
    
    def totalTimeOtherPause(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            if isinstance(cycle, concurrentCycles):
                total += float(cycle.pauseRemark.duration)
                total += float(cycle.pauseCleanup.duration)
        return float("{:.3f}".format(total))
    
    def avgTime(self):
        # in ms
        return self.totalTime() / len(self.cycles)
    
    def toString(self):
        # print the content of the log file
        return self.content
    
    def heapUsage(self):
        # in MB
        heap_usage = []
        for cycle in self.cycles:
            if isinstance(cycle, (pauseFull, pauseYoung)):
                heap_usage.append(cycle.after)
        return heap_usage
    
    def maxHeapUsage(self):
        # in MB
        return max(self.heapUsage())
    
    def minHeapUsage(self):
        # in MB
        return min(self.heapUsage())
    
    def avgHeapUsage(self):
        # in MB
        return sum(self.heapUsage()) / len(self.heapUsage())
    
    def heapUsageAnalysis(self):
        print(f"Total Heap Usage: {sum(self.heapUsage())}M")
        print(f"Average Heap Usage: {self.avgHeapUsage()}M")
        print(f"Min Heap Usage: {self.minHeapUsage()}M")
        print(f"Max Heap Usage: {self.maxHeapUsage()}M")

    def pauseTimeAnalysis(self):
        pause_times = [cycle.duration for cycle in self.cycles]
        total_pause_time = self.totalTime()
        avg_pause_time = total_pause_time / len(pause_times)
        min_pause_time = min(pause_times)
        max_pause_time = max(pause_times)
        print(f"Total Pause Time: {total_pause_time}ms")
        print(f"Average Pause Time: {avg_pause_time}ms")
        print(f"Min Pause Time: {min_pause_time}ms")
        print(f"Max Pause Time: {max_pause_time}ms")

    def write(self, input):
        # Writing to a file
        file = open("result.txt", "w")
        string = input
        file.write(string)
        file.close()

    def stackBarChart(self):
        runtimes = [i.duration for i in self.cycles]

        total_runtime = sum(runtimes)
        percentages = [round((runtime/total_runtime)*100, 2) for runtime in runtimes]

        labels = [str(i) for i in range(len(self.cycles))]

        plt.bar(labels, percentages)

        plt.title('GC Cycles Runtime Percentage')
        plt.ylabel('Percentage of Runtime')
        plt.xlabel('GC Cycle')

        for i, percentage in enumerate(percentages):
            plt.text(i, percentage, f'{percentage}%', ha='center')

        plt.show()

    def timeline(self):
        start_time = 0
        end_time = self.cycles[-1].time_elapsed + self.mstos(self.cycles[-1].duration)

        gc_threads = [(cycle.time_elapsed, (cycle.time_elapsed + self.mstos(cycle.duration))) for cycle in self.cycles]
        rect_height = 1.0
        # colors = ['red', 'green', 'blue']
        # clr=colors[i%3]

        fig, ax = plt.subplots()
        ax.set_ylim(0, len(gc_threads))
        ax.set_xlim(start_time, end_time)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('GC Cycle')
        ax.set_title('Timeline of GC Cycles')

        for i, gc_thread in enumerate(gc_threads):
            gc_patch = mpatches.Rectangle((gc_thread[0], i*rect_height), gc_thread[1]-gc_thread[0], rect_height, color='blue')
            ax.add_patch(gc_patch)

        plt.show()

class pauseYoung:
    def __init__(self, time_elapsed, gc_cycle, gc_type, pause_reason, before, after, total, duration):
        self.time_elapsed = float(time_elapsed)
        self.gc_cycle = gc_cycle
        self.gc_type = gc_type
        self.pause_reason = pause_reason
        self.before = before
        self.after = after
        self.diff = int(before) - int(after)
        self.total = total
        self.duration = float(duration)

class concurrentCycle:
    def __init__(self, time_elapsed_start=0, time_elapsed_end=0, gc_cycle=0, event="", duration=0):
        self.time_elapsed_start = time_elapsed_start
        self.time_elapsed_end = time_elapsed_end
        self.gc_cycle = gc_cycle
        self.event = event
        self.duration = duration

class pauseRemarkCleanup:
    def __init__(self, time_elapsed=0, gc_cycle=0, event='', heap_memory='', before=0, after=0, total=0, duration=0):
        self.time_elapsed = time_elapsed
        self.gc_cycle = gc_cycle
        self.event = event
        self.heap_memory = heap_memory
        self.before = before
        self.after = after
        self.diff = int(before) - int(after)
        self.total = total
        self.duration = float(duration)

class concurrentCycles:
    def __init__(self,concurrentCycle,pauseRemark,pauseCleanup):
        self.concurrentCycle = concurrentCycle
        self.pauseRemark = pauseRemark
        self.pauseCleanup = pauseCleanup
        self.duration = float(concurrentCycle.duration)
        self.time_elapsed = float(concurrentCycle.time_elapsed_end)
        self.gc_cycle = concurrentCycle.gc_cycle

class pauseFull:
    def __init__(self, time_elapsed, gc_cycle, pause_reason, before, after, total, duration):
        self.time_elapsed = float(time_elapsed)
        self.gc_cycle = gc_cycle
        self.pause_reason = pause_reason
        self.before = before
        self.after = after
        self.diff = int(before) - int(after)
        self.total = total
        self.duration = float(duration)

if __name__ == "__main__":
    # Get the argument
    # argument = sys.argv[1]
    # argument = input("Enter the path of the log file: ")

    a = GCLogParser("C:\\spark-app\log\jj\executor-gc.WordCountCached.enwiki-latest-pages-articles.xml.log")
    print(a.totalTimeConcurrentCycle())
    print(a.totalTimePauseTime())
    print(a.totalTimePauseYoung())
    print(a.totalTimePauseFull())
    print(a.totalTimeOtherPause())
    # print(a.cycle(55).duration)
    
    # a.timeline()
