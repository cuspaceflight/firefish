OPENSCAD?=$(shell which openscad)
ifeq ($(OPENSCAD),)
$(error "openscad not found on PATH. Set OPENSCAD variable explicitly")
endif

.PHONY: all
all: cartoon-rocket.stl

%.stl : %.scad
	$(OPENSCAD) -o "$@" "$<"

