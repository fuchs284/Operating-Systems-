import heapq
#pip heapq
class Process:
    def __init__(self, pid, arrival_time, burst_time, memory_required):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.memory_required = memory_required
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = None

    def __repr__(self):
        return (f"P{self.pid}(arrival={self.arrival_time}, burst={self.burst_time}, "
                f"mem={self.memory_required}, start={self.start_time}, complete={self.completion_time})")

class MemoryBlock:
    def __init__(self, start, size):
        self.start = start
        self.size = size
        self.free = True
        self.owner_pid = None  # New field to associate block with process

    def __repr__(self):
        return f"[Start: {self.start}, Size: {self.size}, Free: {self.free}]"

class MemoryManager:
    def __init__(self, total_memory):
        self.memory = [MemoryBlock(0, total_memory)]

    def allocate(self, process, strategy='first_fit'):
        if strategy == 'first_fit':
            return self._first_fit(process)
        elif strategy == 'best_fit':
            return self._best_fit(process)
        return False

    def _first_fit(self, process):
        for block in self.memory:
            if block.free and block.size >= process.memory_required:
                return self._allocate_block(block, process)
        return False

    def _best_fit(self, process):
        candidates = [b for b in self.memory if b.free and b.size >= process.memory_required]
        if not candidates:
            return False
        best = min(candidates, key=lambda b: b.size)
        return self._allocate_block(best, process)

    def _allocate_block(self, block, process):
        if block.size > process.memory_required:
            new_block = MemoryBlock(block.start + process.memory_required, block.size - process.memory_required)
            self.memory.insert(self.memory.index(block) + 1, new_block)
        block.size = process.memory_required
        block.free = False
        block.owner_pid = process.pid
        return True

    def deallocate(self, pid):
        for block in self.memory:
            if not block.free and block.owner_pid == pid:
                block.free = True
                block.owner_pid = None
        self._merge()

    def _merge(self):
        i = 0
        while i < len(self.memory) - 1:
            if self.memory[i].free and self.memory[i + 1].free:
                self.memory[i].size += self.memory[i + 1].size
                del self.memory[i + 1]
            else:
                i += 1

class Scheduler:
    def __init__(self, memory_size, strategy='first_fit'):
        self.memory_manager = MemoryManager(memory_size)
        self.strategy = strategy

    def simulate_fcfs(self, processes):
        time = 0
        processes.sort(key=lambda p: p.arrival_time)  # Sort by arrival time
        completed = []

        for p in processes:
            if time < p.arrival_time:
                time = p.arrival_time
            if not self.memory_manager.allocate(p, self.strategy):
                print(f"Process {p.pid} skipped due to insufficient memory.")
                continue
            p.start_time = time
            time += p.burst_time
            p.completion_time = time
            self.memory_manager.deallocate(p.pid)
            completed.append(p)
        return completed

    def simulate_sjf(self, processes):
        time = 0
        processes.sort(key=lambda p: p.arrival_time)  # Sort by arrival time
        completed = []
        ready_queue = []
        i = 0
        skipped = set()  # Track skipped processes due to memory issues

        while i < len(processes) or ready_queue:
            # Add all processes that have arrived by the current time to the ready queue
            while i < len(processes) and processes[i].arrival_time <= time:
                ready_queue.append(processes[i])
                i += 1

            # If there are processes in the ready queue, sort by burst time (SJF)
            if ready_queue:
                ready_queue.sort(key=lambda p: p.burst_time)  # Sort by burst time (SJF)
                process_to_execute = ready_queue.pop(0)  # Select the process with the shortest burst time

                # Allocate memory for the selected process
                if not self.memory_manager.allocate(process_to_execute, self.strategy):
                    print(f"Process {process_to_execute.pid} skipped due to insufficient memory.")
                    skipped.add(process_to_execute.pid)
                    continue  # Skip this process if memory allocation fails

                # Execute the process
                process_to_execute.start_time = time
                time += process_to_execute.burst_time
                process_to_execute.completion_time = time

                # Deallocate memory after process execution
                self.memory_manager.deallocate(process_to_execute.pid)

                # Add the completed process to the completed list
                completed.append(process_to_execute)

            else:
                # No process is ready to execute, so advance time to the next process arrival
                if i < len(processes):
                    time = processes[i].arrival_time

        return completed

# Example usage:
processes = [
    Process(pid=1, arrival_time=0, burst_time=4, memory_required=50),
    Process(pid=2, arrival_time=1, burst_time=3, memory_required=30),
    Process(pid=3, arrival_time=2, burst_time=2, memory_required=20),
    Process(pid=4, arrival_time=3, burst_time=5, memory_required=100),
    Process(pid=5, arrival_time=4, burst_time=1, memory_required=40)
]

# Scheduler with 150 units of memory and 'first_fit' allocation strategy
scheduler = Scheduler(memory_size=150, strategy='first_fit')

# Simulate SJF scheduling
completed = scheduler.simulate_sjf(processes)

# Print the results
for process in completed:
    print(process)
