OPENSCAD?=$(shell which openscad)
ifeq ($(OPENSCAD),)
$(error "openscad not found on PATH. Set OPENSCAD variable explicitly")
endif

NETGEN?=$(shell which netgen)
ifeq ($(NETGEN),)
$(error "netgen not found on PATH. Set NETGEN variable explicitly")
endif

GMSH?=$(shell which gmsh)
ifeq ($(GMSH),)
$(error "gmsh not found on PATH. Set GMSH variable explicitly")
endif

.PHONY: all
all: cartoon-rocket.domain.msh

%.domain.msh: %.domain.geo %.meshed.surface.stl
	$(GMSH) -format msh -check -o "$@" "$<" -3

%.stl : %.scad
	$(OPENSCAD) -m "$@" "$<"

# Note that netgen sometimes segfaults after generating mesh. Work around this
# by ignoring exit code
%.meshed.surface.stl: %.stl
	-$(NETGEN) -batchmode -meshfiletype="STL Format" \
		-geofile="$<" -meshfile"=$@"
