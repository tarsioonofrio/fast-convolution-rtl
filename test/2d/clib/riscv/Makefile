# Lista dos quatro targets
TARGETS = simple-conv filter1d filter2d-iter filter2d-nest

# Caminho para o make secundário
# MAKE_SUBDIR = caminho/para/o/diretorio/do/Makefile

# Regra para cada target
all: $(TARGETS)

$(TARGETS):
	@if [ -f $(MAKE_SUBDIR)/$@.c ]; then \
		$(MAKE) common.mk TARGET=$@; \
	else \
		echo "Arquivo $(MAKE_SUBDIR)/$@.c não encontrado. Pulando..."; \
	fi

.PHONY: all $(TARGETS)

clean:
	$(MAKE) common.mk clean;
