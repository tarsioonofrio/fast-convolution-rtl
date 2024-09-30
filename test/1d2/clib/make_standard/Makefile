
        TARGET   ?= standard
        OPT      ?= 0
        GCCOPT   ?= O2
        SRCDIR   ?= $(CURDIR)/../src
        ARCH     ?= rv32im_zicsr
        MEM_SIZE ?= 65536

        SRCDIR   ?= make_standard ../src
        INCDIR = $(SRCDIR)/data:$(SRCDIR)/lib/include"

        P1 = $(CURDIR)/../common/common/.mk
        P2 = $(CURDIR)/../$(P1)
        COMMDIR ?= $(if $(wildcard $(P1)),$(P1),$(if $(wildcard $(P2)),$(P2),))
        include $(COMMDIR)"
    