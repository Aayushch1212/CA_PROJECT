import m5
from m5.objects import Cache

# Add the common scripts to our path
m5.util.addToPath("../../")

# Base L1 Cache class with common attributes
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    #def __init__(self, version=None, options=None):
    #    super().__init__()

    def connectCPU(self, cpu):
        raise NotImplementedError

    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

# L1-Instruction Cache
class L1ICache(L1Cache):
    size = '16kB'
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    
    def connectCPU(self,cpu):
        self.cpu_side = cpu.icache_port

# L1-Data Cache
class L1DCache(L1Cache):
    size = '16kB'
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    
    def connectCPU(self,cpu):
        self.cpu_side = cpu.dcache_port

# L2 Cache
class L2Cache(Cache):
    size = "256kB"
    assoc = 4
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 10
    tgts_per_mshr = 6


    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports

