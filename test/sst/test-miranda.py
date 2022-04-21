# Automatically generated SST Python input
import sst

# Define the simulation components
cores = 1
coreclock = "2.4GHz"
uncoreclock = "1.4GHz"
coherence = "MESI"
network_bw = "60GB/s"
numGUPSiter = 10000
KiB = 1024
MiB = KiB * 1024
l1size = 2 #"KiB"
memsize = 512 #"MiB"
DEBUG = 0


# Create merlin network - this is just simple single router
comp_network = sst.Component("network", "merlin.hr_router")
comp_network.addParams({
      "xbar_bw" : network_bw,
      "link_bw" : network_bw,
      "input_buf_size" : "2KiB",
      "num_ports" : cores + 2,
      "flit_size" : "36B",
      "output_buf_size" : "2KiB",
      "id" : "0",  
      "topology" : "merlin.singlerouter"
})
comp_network.setSubComponent("topology","merlin.singlerouter")



for x in range(cores):
    # Define the simulation components
    comp_cpu = sst.Component("cpu" + str(x), "miranda.BaseCPU")
    comp_cpu.addParams({
        "verbose" : DEBUG,
    })
    gen = comp_cpu.setSubComponent("generator", "miranda.GUPSGenerator")
    gen.addParams({
        "verbose" : DEBUG,
        "count" : numGUPSiter,
        "max_address" : memsize * MiB,
    })
    iface = comp_cpu.setSubComponent("memory", "memHierarchy.memInterface")

    l1cache = sst.Component("l1cache" + str(x), "memHierarchy.Cache")
    l1cache.addParams({
        "cache_frequency" : coreclock,
        "access_latency_cycles" : 3,
        "replacement_policy" : "lru",
        "coherence_protocol" : coherence,
        "cache_size" : str(l1size) + "KiB",  # super tiny for lots of traffic
        "associativity" : 2,
        "L1" : 1,
        "debug" : DEBUG,
        "debug_level" : 10,
    })
    l1toC = l1cache.setSubComponent("cpulink", "memHierarchy.MemLink")
    l1NIC = l1cache.setSubComponent("memlink", "memHierarchy.MemNIC")
    l1NIC.addParams({
        "group" : 1,
        "network_bw" : network_bw,
    })

    cpu_l1_link = sst.Link("link_cpu_cache_" + str(x))
    cpu_l1_link.connect ( (iface, "port", "500ps"), (l1toC, "port", "500ps") )

    l1_network_link = sst.Link("link_l1_network_" + str(x))
    l1_network_link.connect( (l1NIC, "port", "100ps"), (comp_network, "port" + str(x), "100ps") )



# directory controller coordinates where memory traffic goes on the network?
dirctrl = sst.Component("directory", "memHierarchy.DirectoryController")
dirctrl.addParams({
	"clock" : uncoreclock,
	"coherence_protocol" : coherence,
	"entry_cache_size" : 32768,
	"debug" : DEBUG,
	"debug_level" : 10,
	"addr_range_start" : 0,
	"addr_range_end" :  memsize * MiB
})
dirNIC = dirctrl.setSubComponent("cpulink", "memHierarchy.MemNIC")
dirNIC.addParams({
	"group" : 2,
	"network_bw" : network_bw,
	"network_input_buffer_size" : "2KiB",
	"network_output_buffer_size" : "2KiB",
	"debug" : DEBUG,
	"debug_level" : 10,
})


# Setup a simpleDRAM memory with controller connected to the network
memctrl = sst.Component("memory", "memHierarchy.MemController")
memctrl.addParams({
	"clock" : "500MHz",
	"backing" : "none",
	"debug" : DEBUG,
	"debug_level" : 10,
	"addr_range_start" : 0,
	"addr_range_end" :  memsize * MiB
})
memNIC = memctrl.setSubComponent("cpulink", "memHierarchy.MemNIC")
memNIC.addParams({
	"group" : 3,
	"network_bw" : network_bw,
	"network_input_buffer_size" : "2KiB",
	"network_output_buffer_size" : "2KiB",
    "debug" : DEBUG,
	"debug_level" : 10,
})

memory = memctrl.setSubComponent("backend", "memHierarchy.simpleDRAM")
memory.addParams({
	"mem_size" : str(memsize) + "MiB",
	"tCAS" : 2,
	"tRCD" : 2,
	"tRP" : 3,
	"cycle_time" : "3ns",
	"row_size" : "4KiB",
	"row_policy" : "closed",
	"max_requests_per_cycle" : 2,
})

portid = cores
link_directory_network = sst.Link("link_directory_network")
link_directory_network.connect( (dirNIC, "port", "100ps"), (comp_network, "port" + str(portid), "100ps") )

portid += 1
link_memory_network = sst.Link("link_memory_network")
link_memory_network.connect( (memNIC, "port", "100ps",), (comp_network, "port" + str(portid), "100ps") )


# Enable statistics
sst.setStatisticLoadLevel(16)
sst.enableAllStatisticsForAllComponents({"type": "sst.AccumulatorStatistic"})
sst.setStatisticOutput("sst.statOutputCSV")
sst.setStatisticOutputOptions({
    "filepath" : "stats.csv",
    "separator" : ", ",
    })
