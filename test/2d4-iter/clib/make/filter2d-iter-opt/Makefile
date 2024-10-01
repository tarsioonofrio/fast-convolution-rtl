TARGET   ?= filter2d-iter
OPTIM    ?= 1
GCCOPT   ?= O2
SRCDIR   ?= $(realpath $(CURDIR)/../../src)
ARCH     ?= rv32im_zicsr
MEM_SIZE ?= 65536

# add more src files
SRCPATH  = $(SRCDIR)/lib $(CURDIR)/lib
SRCFILES = $(SRCDIR)/main/$(TARGET).c $(foreach dir,$(SRCPATH),$(wildcard $(dir)/*.c))

# add more header files
INCPATH  = $(SRCDIR)/data $(SRCDIR)/lib/include $(CURDIR)/lib/include
INCFILES = $(foreach dir,$(INCPATH),$(wildcard $(dir)/*.h))
INCFLAGS = $(foreach dir,$(INCPATH),-I$(dir))

# search for common files in two levels above
MAKECOMM = $(realpath $(CURDIR)/../../common/common.mk)
COMMDIR  ?= $(dir $(MAKECOMM))

include $(MAKECOMM)
