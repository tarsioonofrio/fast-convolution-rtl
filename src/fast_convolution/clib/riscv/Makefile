# Lista dos quatro targets
TARGETS = simple-conv filter1d filter2d-iter filter2d-nest

# Caminho para o make secundário
# MAKE_SUBDIR = caminho/para/o/diretorio/do/Makefile

# Regra para cada target
all: $(TARGETS)

$(TARGETS):
	@if [ -f ../src/$@.c ]; then \
		$(MAKE) -f common.mk TARGET=$@; \
	else \
		echo "Arquivo ../src/$@.c não encontrado. Pulando..."; \
	fi

.PHONY: all $(TARGETS)

clean:
	$(MAKE) -f common.mk clean;
