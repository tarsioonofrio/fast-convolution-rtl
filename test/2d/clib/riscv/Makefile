RED  =\033[0;31m
NC   =\033[0m # No Color

TARGET1  ?= fast-conv
TARGET2  ?= simple-conv
MEM_SIZE ?= 65536
ARCH     ?= rv32im

CC 		= riscv64-elf-gcc
OBJDUMP = riscv64-elf-objdump
OBJCOPY = riscv64-elf-objcopy

SRCDIR  = ../src
LIBDIR  = $(SRCDIR)/lib
INCDIR  = $(LIBDIR)/include
DATADIR = $(SRCDIR)/data
HEADERS = $(wildcard $(INCDIR)/*.h) $(wildcard $(DATADIR)/*.h)

CFLAGS  = -march=$(ARCH) -mabi=ilp32 -Os -Wall -std=c23 -I$(INCDIR) -I$(DATADIR)
LDFLAGS = --specs=nano.specs -T common/link.ld -march=$(ARCH) -mabi=ilp32 -nostartfiles

# CCSRC1 = $(wildcard $(SRCDIR)/*.c) $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCSRC1 = $(SRCDIR)/$(TARGET1).c $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCOBJ1 = $(patsubst %.c, %.o, $(CCSRC1))

CCSRC2 = $(SRCDIR)/$(TARGET2).c $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCOBJ2 = $(patsubst %.c, %.o, $(CCSRC2))

ASSRC = $(wildcard common/*.S)
ASOBJ = $(patsubst %.S,%.o, $(ASSRC))

all: $(TARGET1).bin $(TARGET1).lst $(TARGET2).bin $(TARGET2).lst

$(TARGET1).bin: $(TARGET1).elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

$(TARGET1).lst: $(TARGET1).elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJDUMP) -S $< > $@

$(TARGET1).elf: $(CCOBJ1) $(ASOBJ)
	@printf "${RED}Linking %s...${NC}\n" "$@"
	@$(CC) $(CCOBJ1) $(ASOBJ) -Wl,-Map=$(TARGET1).map -N -o $@ $(LDFLAGS)

$(TARGET2).bin: $(TARGET2).elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

$(TARGET2).lst: $(TARGET2).elf
	@printf "${RED}Generating %s...${NC}\n" "$@"
	@$(OBJDUMP) -S $< > $@

$(TARGET2).elf: $(CCOBJ2) $(ASOBJ)
	@printf "${RED}Linking %s...${NC}\n" "$@"
	@$(CC) $(CCOBJ2) $(ASOBJ) -Wl,-Map=$(TARGET2).map -N -o $@ $(LDFLAGS)

%.o: %.S
	@printf "${RED}Assemblying %s...${NC}\n" "$<"
	@$(CC) -c $< -o $@ $(CFLAGS) -march=$(ARCH)_zicsr -DMEM_SIZE=$(MEM_SIZE)

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
