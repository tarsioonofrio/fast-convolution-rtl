TARGET0 = simple-conv
TARGET1 = filter1d
MEM_SIZE ?= 65536
ARCH     ?= rv32im_zicsr

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


%.o: %.S
	@printf "$Assemblying %s...$\n" "$<"
	@$(CC) -c $< -o $@ $(CFLAGS) -march=$(ARCH) -DMEM_SIZE=$(MEM_SIZE) -DRISCV=1

%.o: %.c $(HEADERS)
	@printf "$Compiling %s...$\n" "$<"
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

all:$(TARGET0).bin $(TARGET0).lst $(TARGET1).bin $(TARGET1).lst
CCSRC0 = $(SRCDIR)/$(TARGET0).c $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCOBJ0 = $(patsubst %.c, %.o, $(CCSRC0))


$(TARGET0).bin: $(TARGET0).elf
	@printf "$Generating %s...$\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

$(TARGET0).lst: $(TARGET0).elf
	@printf "$Generating %s...$\n" "$@"
	@$(OBJDUMP) -S $< > $@

$(TARGET0).elf: $(CCOBJ0) $(ASOBJ)
	@printf "$Linking %s...$\n" "$@"
	@$(CC) $(CCOBJ0) $(ASOBJ) -Wl,-Map=$(TARGET0).map -N -o $@ $(LDFLAGS)

CCSRC1 = $(SRCDIR)/$(TARGET1).c $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCOBJ1 = $(patsubst %.c, %.o, $(CCSRC1))


$(TARGET1).bin: $(TARGET1).elf
	@printf "$Generating %s...$\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

$(TARGET1).lst: $(TARGET1).elf
	@printf "$Generating %s...$\n" "$@"
	@$(OBJDUMP) -S $< > $@

$(TARGET1).elf: $(CCOBJ1) $(ASOBJ)
	@printf "$Linking %s...$\n" "$@"
	@$(CC) $(CCOBJ1) $(ASOBJ) -Wl,-Map=$(TARGET1).map -N -o $@ $(LDFLAGS)
