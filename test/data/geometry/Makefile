OPENSCAD?=$(shell which openscad)
ifeq ($(OPENSCAD),)
$(error "openscad not found on PATH. Set OPENSCAD variable explicitly")
endif

STL_FILES:=unit_sphere.stl

.PHONY: all
all: $(STL_FILES)

.PHONY: clean
clean:
	rm -f $(STL_FILES)

%.stl : %.scad
	$(OPENSCAD) -o "$@" "$<"
