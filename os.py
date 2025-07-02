import heapq

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
        processes.sort(key=lambda p: p.arrival_time)
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
        queue = []
        completed = []
        processes.sort(key=lambda x: x.arrival_time)
        i = 0
        skipped = set()