# Lista dos quatro targets
TARGETS = simple-conv filter1d filter2d-iter filter2d-nest
TARGETS_OPTIM = filter1d filter2d-iter
TARGETS_OPTIM_ITER = filter2d-nest

# Caminho para o make secundário
# MAKE_SUBDIR = caminho/para/o/diretorio/do/Makefile

# Regra para cada target
all: $(TARGETS) filter1d-optim filter2d-nest-optim filter2d-iter-optim

$(TARGETS):
	@if [ -f ../src/$@.c ]; then \
		$(MAKE) -f common.mk TARGET=$@; \
	else \
		echo "Arquivo ../src/$@.c não encontrado. Pulando..."; \
	fi

filter1d-optim:
	@if [ -f ../src/filter1d.c ]; then \
		$(MAKE) -f common.mk TARGET_FILE=filter1d TARGET=filter2d-nest-optim OPTIM=1; \
	else \
		echo "Arquivo ../src/$@.c não encontrado. Pulando..."; \
	fi

filter2d-nest-optim:
	@if [ -f ../src/filter2d-nest.c ]; then \
		$(MAKE) -f common.mk TARGET_FILE=filter2d-nest TARGET=filter2d-nest-optim OPTIM=1; \
	else \
		echo "Arquivo ../src/$@.c não encontrado. Pulando..."; \
	fi

filter2d-iter-optim:
	@if [ -f ../src/filter2d-iter.c ]; then \
		$(MAKE) -f common.mk TARGET_FILE=filter2d-iter TARGET=filter2d-iter-optim OPTIM=1 OPTIM_ITER=1; \
	else \
		echo "Arquivo ../src/$@.c não encontrado. Pulando..."; \
	fi

.PHONY: all $(TARGETS)

clean:
	$(MAKE) -f common.mk clean;
