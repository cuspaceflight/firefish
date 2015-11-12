// design values - length units are mm
body_height = 1000;
body_diameter = 100;
fin_count=3;

// number of flat facets to use to represent a
// cylinder
resolution = 25;

// values derived from above which can be tweaked
cone_height = 3*body_diameter;
fin_extent = 0.5*body_diameter;
fin_flat_height = 0.2*body_height;
fin_raked_height = fin_flat_height;
fin_thickness = 0.1 * body_diameter;

// derived values which shouldn't be tweaked
body_radius = 0.5 * body_diameter;

// a module which represents a rocket fin
module fin(angle=0) {
    rotate([0, 0, angle])
    hull() {
        translate([0, -0.5*fin_thickness, 0]) {
            cube([
                body_radius + fin_extent, 
                fin_thickness,
                fin_flat_height
            ]);
            cube([
                body_radius, 
                fin_thickness,
                fin_flat_height + fin_raked_height
            ]);
        }
    };
};

// the main rocket itself is the union of the body,
// cone and fins.
translate([0, 0, -0.5*(body_height + cone_height)]) {
    union() {
        cylinder(
            $fn=resolution,
            h=body_height, r=body_radius
        );

        translate([0, 0, body_height]) {
            cylinder(
                $fn=resolution,
                h=cone_height, r1=body_radius, r2=0
            );
        }
        
        fin_inc = 360 / fin_count;
        for(a=[0:fin_inc:360-fin_inc]) {
            fin(angle=a);
        }
    }
}
