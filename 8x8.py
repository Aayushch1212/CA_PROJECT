import m5
from m5.objects import *
from cache import *
from m5.defines import buildEnv
from m5.util import addToPath
import os, argparse, sys

# Add necessary paths
addToPath('../')
addToPath('../topologies')  # Path for Mesh_XY.py

# Import modules
from common import Options
from ruby import Ruby
from topologies.Mesh_XY import Mesh_XY  # Import Mesh_XY topology

# Create the command line parser
parser = argparse.ArgumentParser()

# Add the ruby specific and protocol specific options
Options.addNoISAOptions(parser)
Ruby.define_options(parser)

# Add mesh topology options (required by Mesh_XY)
parser.add_argument('--num_cpus', type=int, default=64,
                    help="Number of CPUs")
parser.add_argument('--mesh_rows', type=int, default=8,
                    help="Number of rows in the mesh")
parser.add_argument('--link_latency', type=int, default=1,
                    help="Latency for each link in the network")
parser.add_argument('--router_latency', type=int, default=1,
                    help="Latency of each router in the network")

# Parse the command line options
args = parser.parse_args()

# Create the system
system = System()

# Initialise a clock and voltage domain
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz' # Gem5 can convert units automatically
system.clk_domain.voltage_domain = VoltageDomain()

# Creating memory for system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8192MB')] # 8GB memory is assigned

# Create CPU clusters
system.cpu = [TimingSimpleCPU(cpu_id=i+100) for i in range(args.num_cpus)]
for cpu in system.cpu:
    cpu.createThreads()
    cpu.createInterruptController()

# Create the Ruby system
Ruby.create_system(args, False, system)

# Create L1 cache controllers
l1_cache_controllers = []
for i in range(args.num_cpus):
    l1_cache_controller = L1Cache_Controller(version=i)
    l1_cache_controller.ruby_system = system.ruby
    l1_cache_controllers.append(l1_cache_controller)

# Create L2 cache controllers (2 shared L2 caches)
l2_cache_controllers = []
for i in range(2):
    l2_cache = L2Cache_Controller(version=i)
    l2_cache.ruby_system = system.ruby
    l2_cache_controllers.append(l2_cache)

# Create directory controllers
dir_controllers = []
for i in range(2):
    dir_ctrl = Directory_Controller(version=i)
    dir_ctrl.directory = RubyDirectoryMemory()
    dir_ctrl.ruby_system = system.ruby
    dir_controllers.append(dir_ctrl)

# Combine all controllers
controllers = l1_cache_controllers + l2_cache_controllers + dir_controllers

# Create the network using Mesh_XY topology
mesh_topology = Mesh_XY(controllers)  # Pass the controllers to the Mesh_XY class
mesh_topology.makeTopology(args, system.ruby.network, SimpleIntLink, SimpleExtLink, BasicRouter)

# Set up the system topology with system
mesh_topology.registerTopology(args)

# Assign binary and its input to the process
binary = 'tests/test-progs/hello/bin/x86/linux/hello'
system.workload = SEWorkload.init_compatible(binary)
process = Process()
process.cmd = [binary]  # Binary and input file (no input in hello world)

# Assign the process as the workload for each CPU
for cpu in system.cpu:
    cpu.workload = process

# Set up a root to top of the hierarchy
root = Root(full_system = False, system = system)

# Instantiate the system
m5.instantiate()

# Run the simulation
print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))

