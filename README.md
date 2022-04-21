# SST Juno Processor Model

Juno is a very lightweight processor model which executes programs written
in a simple assembly. The processor is designed to be easily extensible and used
as an SST example element/component.

The SST project team use Juno to perform some simple (but fast) correctness checks
of the SST memory hierarchy, network-on-chip and memory sub-system modeling.

Questions? Email: wg-sst@sandia.gov

### General instructions to compile and run

1. Pre-requisites required to run Juno example  
```text
- SST-core and SST-elements (10.0+) installed
- All respective enviornment variables initiallized
```  

2. Download this Juno git repo in your `$HOME/scratch/src/` folder  
3. Go into `asm` folder to build assembler for Juno.  
```bash
cd asm
make
```

4. Go into `src` folder to build Juno SST component  
```bash
cd ../src
make
```

5. Compile the GUPS program  
```bash
cd ../test/asm
../../asm/sst-juno-asm -i gups.juno -o gups.bin"
```

6. Run SST to simulate GUPS on Juno processor
```bash
cd ../sst
sst juno-test.py
```  

_**Note:**_ `juno-test.py` is the python file with system-config information where you can change parameters like `CPU frequency`, `memory frequency`, `cache size`, etc.  
