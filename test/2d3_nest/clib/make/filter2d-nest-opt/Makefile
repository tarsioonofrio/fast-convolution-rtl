TARGET   ?= filter2d-nest
OPTIM    ?= 1
GCCOPT   ?= O2
SRCDIR   ?= $(realpath $(CURDIR)/../../src)
ARCH     ?= rv32im_zicsr
MEM_SIZE ?= 65536

# add more src files
SRCPATH  = $(SRCDIR)/lib $(SRCDIR)/lib_opt
SRCFILES =  $(SRCDIR)/main/$(TARGET).c $(foreach dir,$(SRCPATH),$(wildcard $(dir)/*.c))

# add more header files
INCPATH  = $(SRCDIR)/data $(SRCDIR)/lib/include $(SRCDIR)/lib_opt/include
INCFILES = $(foreach dir,$(INCPATH),$(wildcard $(dir)/*.h))
INCFLAGS = $(foreach dir,$(INCPATH),-I$(dir))

# search for common files in two levels above
P1 = $(realpath $(CURDIR)/../../common/common.mk)
P2 = $(realpath $(CURDIR)/../$(P1))
COMMFILE ?= $(if $(wildcard $(P1)),$(P1),$(if $(wildcard $(P2)),$(P2),))
COMMDIR  ?= $(dir $(COMMFILE))

include $(COMMFILE)
