def makefile(files):
    files_str = "\n".join([f"TARGET{e} = {n}" for e, n in enumerate(files)])
    all_str = " ".join(
        [f"all: $(TARGET{e}).bin $(TARGET{e}).lst" for e, n in enumerate(files)]
    )
    targets_str = "\n".join(
        [makefile_target.format(target=e) for e, n in enumerate(files)]
    )
    makefile_str = (
        files_str + "\n" + makefile_base + "\n" + all_str + "\n" + targets_str
    )
    return makefile_str


# TARGET1  ?= fast-conv
# TARGET2  ?= simple-conv

makefile_base = """
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
"""

# all: $(TARGET1).bin $(TARGET1).lst
makefile_target = """
CCSRC{target} = $(SRCDIR)/$(TARGET{target}).c $(wildcard $(LIBDIR)/*.c) $(wildcard common/*.c)
CCOBJ{target} = $(patsubst %.c, %.o, $(CCSRC{target}))


$(TARGET{target}).bin: $(TARGET{target}).elf
	@printf "$Generating %s...$\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

$(TARGET{target}).lst: $(TARGET{target}).elf
	@printf "$Generating %s...$\n" "$@"
	@$(OBJDUMP) -S $< > $@

$(TARGET{target}).elf: $(CCOBJ{target}) $(ASOBJ)
	@printf "$Linking %s...$\n" "$@"
	@$(CC) $(CCOBJ{target}) $(ASOBJ) -Wl,-Map=$(TARGET{target}).map -N -o $@ $(LDFLAGS)
"""
