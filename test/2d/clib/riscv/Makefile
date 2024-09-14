RED  =\033[0;31m
NC   =\033[0m # No Color

ROOTDIR  = ./
TARGET  ?= simple-conv
GCCOPT  ?= s
OPTIM   ?= 0

MEM_SIZE ?= 65536
ARCH     ?= rv32im_zicsr

CC 		= riscv64-elf-gcc
OBJDUMP = riscv64-elf-objdump
OBJCOPY = riscv64-elf-objcopy

SRCDIR  = ${ROOTDIR}/src
COMDIR  = ${ROOTDIR}/riscv/common
LIBDIR  = $(SRCDIR)/lib
INCDIR  = $(LIBDIR)/include
DATADIR = $(SRCDIR)/data
HEADERS = $(wildcard $(INCDIR)/*.h) $(wildcard $(DATADIR)/*.h) $(wildcard ${COMDIR}/include/*.h)

CFLAGS  = -march=$(ARCH) -mabi=ilp32 -O${GCCOPT} -Wall -std=c23 -I$(INCDIR) -I$(DATADIR) -I${COMDIR}/include
LDFLAGS = --specs=nano.specs -T ${COMDIR}/link.ld -march=$(ARCH) -mabi=ilp32 -nostartfiles

CCSRC = $(SRCDIR)/$(TARGET).c $(wildcard $(LIBDIR)/*.c) $(wildcard ${COMDIR}/*.c)
CCOBJ = $(patsubst %.c, %.o, $(CCSRC))


ASSRC = $(wildcard ${COMDIR}/*.S)
ASOBJ = $(patsubst %.S,%.o, $(ASSRC))

all: $(TARGET).bin $(TARGET).lst

$(TARGET).bin: $(TARGET).elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJCOPY) $<  ${ROOTDIR}/$@ -O binary

$(TARGET).lst: $(TARGET).elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJDUMP) -S $< >  ${ROOTDIR}/$@

$(TARGET).elf: $(CCOBJ) $(ASOBJ)
	@printf "${RED}Linking %s...${NC}\n" "$@"
	@$(CC) $(CCOBJ) $(ASOBJ) -Wl,-Map=$(TARGET).map -N -o  ${ROOTDIR}/$@ $(LDFLAGS)

%.o: %.S
	@printf "${RED}Assemblying %s...${NC}\n" "$<"
	@$(CC) -c $< -o $@ $(CFLAGS) -march=$(ARCH) -DMEM_SIZE=$(MEM_SIZE) -DRISCV=1

%.o: %.c $(HEADERS)
	@printf "${RED}Compiling %s...${NC}\n" "$<"
	@$(CC) -c $< -o $@ $(CFLAGS)

clean:
	@printf "Cleaning up\n"
	@rm -rf src/*.o
	@rm -rf src/lib/*.o
	@rm -rf common/*.o
	@rm -rf *.bin
	@rm -rf *.map
	@rm -rf *.lst
	@rm -rf *.elf

.PHONY: clean
