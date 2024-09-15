RED  =\033[0;31m
NC   =\033[0m # No Color

# $(info INCDIR_CONV: ${INCDIR_CONV})

CLIBDIR ?= $(CURDIR)
TARGET  ?= simple-conv
GCCOPT  ?= s
OPTIM   ?= 0

MEM_SIZE ?= 65536
ARCH     ?= rv32im_zicsr

CC 		= riscv64-elf-gcc
OBJDUMP = riscv64-elf-objdump
OBJCOPY = riscv64-elf-objcopy


COMMDIR = $(CLIBDIR)/riscv/common
SRCDIR  = $(CLIBDIR)/src

LIBDIR_CONV  = $(SRCDIR)/lib/conv
LIB_FAST  = $(SRCDIR)/lib/fast/fast_conv.c
# LIBDIR_OPT  = $(SRCDIR)/lib/fast_optim/fast_conv.c

# INCDIR  = $(SRCDIR)/include
INCDIR_CONV  = $(SRCDIR)/include/conv
INCDIR_FAST  = $(SRCDIR)/include/fast
# INCDIR_OPT  = $(SRCDIR)/include/fast_optim

DATADIR = $(SRCDIR)/data
HEADERS = $(wildcard $(COMMDIR)/include/*.h) $(wildcard $(DATADIR)/*.h) $(wildcard $(INCDIR_CONV)/*.h) $(INCDIR_FAST)/fast_conv.h

CFLAGS  = -march=$(ARCH) -mabi=ilp32 -O$(GCCOPT) -Wall -std=c23 -I$(COMMDIR)/include -I$(DATADIR) -I$(INCDIR_CONV) -I$(INCDIR_FAST) 
LDFLAGS = --specs=nano.specs -T $(COMMDIR)/link.ld -march=$(ARCH) -mabi=ilp32 -nostartfiles

CCSRC = $(SRCDIR)/$(TARGET).c $(wildcard $(COMMDIR)/*.c) $(wildcard $(LIBDIR_CONV)/*.c) $(LIB_FAST)
CCOBJ = $(patsubst %.c, %.o, $(CCSRC))


ASSRC = $(wildcard $(COMMDIR)/*.S)
ASOBJ = $(patsubst %.S,%.o, $(ASSRC))

all: $(TARGET).bin $(TARGET).lst

$(TARGET).bin: $(TARGET).elf
	@printf "$(RED)Generating %s...$(NC)\n" "$@"
	@$(OBJCOPY) $< $@ -O binary

$(TARGET).lst: $(TARGET).elf
	@printf "$(RED)Generating %s...$(NC)\n" "$@"
	@$(OBJDUMP) -S $< > $@

$(TARGET).elf: $(CCOBJ) $(ASOBJ)
	@printf "$(RED)Linking %s...$(NC)\n" "$@"
	@$(CC) $(CCOBJ) $(ASOBJ) -Wl,-Map=$(TARGET).map -N -o $@ $(LDFLAGS)


%.o: %.S
	@printf "$(RED)Assemblying %s...$(NC)\n" "$<"
	@$(CC) -c $< -o $@ $(CFLAGS) -march=$(ARCH) -DMEM_SIZE=$(MEM_SIZE) -DRISCV=1

%.o: %.c $(HEADERS)
	@printf "$(RED)Compiling %s...$(NC)\n" "$<"
	@$(CC) -c $< -o $@ $(CFLAGS)

clean:
	@printf "Cleaning up\n"
	@rm -rf $(CLIBDIR)/common/*.o
	@rm -rf *.bin
	@rm -rf *.map
	@rm -rf *.lst
	@rm -rf *.elf
	@find $(SRCDIR) -type f -name "*.o" -delete

.PHONY: clean
