RED  =\033[0;31m
NC   =\033[0m # No Color

FILE_NAME ?= $(basename $(notdir $(wildcard ../src/*.c)))

$(info  $(FILE_NAME))

MEM_SIZE  ?= 65536
ARCH      ?= rv32im_zicsr

CC 		= riscv64-elf-gcc
OBJDUMP = riscv64-elf-objdump
OBJCOPY = riscv64-elf-objcopy

SRCDIR  = ../src
LIBDIR  = $(SRCDIR)/lib
INCDIR  = $(LIBDIR)/include
DATADIR = $(SRCDIR)/data
HEADERS = $(wildcard $(INCDIR)/*.h) $(wildcard $(DATADIR)/*.h) $(wildcard ../common/include/*.h)

CFLAGS  = -march=$(ARCH) -mabi=ilp32 -Os -Wall -std=c23 -I$(INCDIR) -I$(DATADIR) -I./common/include
LDFLAGS = --specs=nano.specs -T common/link.ld -march=$(ARCH) -mabi=ilp32 -nostartfiles

ASSRC = $(wildcard common/*.S)
ASOBJ = $(patsubst %.S,%.o, $(ASSRC))

CCSRC = $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCOBJ = $(patsubst %.c, %.o, $(CCSRC))

all: $(foreach file, $(FILE_NAME), $(file).bin $(file).lst)
# all: $(FILE_NAME).bin $(FILE_NAME).lst

%.bin: %.elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

%.lst: %.elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJDUMP) -S $< > $@

%.elf: %.o $(CCOBJ) $(ASOBJ)  
	@printf "${RED}Linking %s...${NC}\n" "$@"
	@$(CC) $(CCOBJ) $(SRCDIR)/$(basename $@).o $(CCOBJ) $(ASOBJ) -Wl,-Map=$@.map -N -o $@ $(LDFLAGS)

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
