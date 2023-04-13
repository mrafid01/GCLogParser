import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class GCLogParser:
    pauseYoung_pattern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc\s*\] GC\((\d+)\) Pause Young \(([^)]+)\) \(([^)]+)\) (\d+)M->(\d+)M\((\d+)M\) (\d+\.\d+)ms$"
    concurrentCycle_patttern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc\s*\] GC\((\d+)\) (Concurrent Cycle|Pause Remark|Pause Cleanup)( (\d+)M->(\d+)M\((\d+)M\))?( (\d+\.\d+)ms)?$"
    heapConsumption_pattern = r"^\[(\d+\.\d+)s\]\[info\s*\]\[gc,heap\s*\] GC\((\d+)\) (Eden regions|Survivor regions|Old regions|Humongous regions): (\d+)->(\d+)(\((\d+)\))?$"

    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.content = file.read()
            self.lines = self.content.split("\n")
        self.cycles= {}
        self.__build()
        self.cycles = list(dict(sorted(self.cycles.items())).values())

    def __build(self):
        self.parse_pauseYoung()
        self.parse_conccurentCycle()

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

                a = pauseYoung(time_elapsed, gc_cycle, gc_type, pause_reason, before, after, total, duration)
                self.cycles[gc_cycle] = a

    def parse_conccurentCycle(self):
        i = None
        concurrentCycleTmp = None
        PauseRemarkTmp = None
        PauseCleanupTmp = None
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
                    if i == gc_cycle and concurrentCycleTmp is not None:
                        concurrentCycleTmp.time_elapsed_end = time_elapsed
                        concurrentCycleTmp.duration = duration
                        a = concurrentCycles(concurrentCycleTmp, PauseRemarkTmp, PauseCleanupTmp)
                        self.cycles[gc_cycle] = a
                    else:
                        concurrentCycleTmp = concurrentCycle(time_elapsed, 0.0, gc_cycle, event, duration)
                        i = gc_cycle
                        continue
                if i == gc_cycle:
                    if event == "Pause Remark":
                        PauseRemarkTmp = PauseRemarkCleanup(time_elapsed, gc_cycle, event, heap_memory, before, after, total, duration)
                        continue
                    elif event == "Pause Cleanup":
                        PauseCleanupTmp = PauseRemarkCleanup(time_elapsed, gc_cycle, event, heap_memory, before, after, total, duration)
                        continue

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
    
    def totalTimePauseYoung(self):
        # in ms
        total = 0
        for cycle in self.cycles:
            if isinstance(cycle, pauseYoung):
                total += cycle.duration
        return float("{:.3f}".format(total))
    
    def avgTime(self):
        # in ms
        return float("{:.3f}".format(self.totalTime() / len(self.cycles)))
    
    def toString(self):
        # print the content of the log file
        return self.content
    
    def minPauseTime(self):
        pause_times = [cycle.duration for cycle in self.cycles]
        return min(pause_times)

    def maxPauseTime(self):
        pause_times = [cycle.duration for cycle in self.cycles]
        return max(pause_times)

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

    def stackBarChart(self, show=True, file_path=None):
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
        
        if show:
            plt.show()
        elif file_path is None:
            plt.savefig('stackBarChart.png')
        else:
            plt.savefig(file_path + '-stackBarChart.png')

        plt.clf()

    def timeline(self, show=True, file_path=None):
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

        if show:
            plt.show()
        elif file_path is None:
            plt.savefig('timeline.png')
        else:
            plt.savefig(file_path + '-timeline.png')

        plt.clf()

    def test(self):
        pass

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
    def __init__(self, time_elapsed_start, time_elapsed_end, gc_cycle, event, duration):
        self.time_elapsed_start = time_elapsed_start
        self.time_elapsed_end = time_elapsed_end
        self.gc_cycle = gc_cycle
        self.event = event
        self.duration = duration

class PauseRemarkCleanup:
    def __init__(self, time_elapsed, gc_cycle, event, heap_memory, before, after, total, duration):
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
    def __init__(self,concurrentCycle,PauseRemarkCleanup1,pauseRemarkCleanup2):
        self.concurrentCycle = concurrentCycle
        self.PauseRemark = PauseRemarkCleanup1
        self.PauseCleanup = pauseRemarkCleanup2
        self.duration = float(concurrentCycle.duration)
        self.time_elapsed = float(concurrentCycle.time_elapsed_end)
        self.gc_cycle = concurrentCycle.gc_cycle

if __name__ == "__main__":
    # Get the argument
    # argument = sys.argv[1]
    # argument = input("Enter the path of the log file: ")

    a = GCLogParser("./Backend/SavedFiles/executor-gc.log")
    print(a.totalTimeConcurrentCycle())
    print(a.totalTimePauseYoung())
    # print(a.cycle(55).duration)
    
    # a.timeline()
