// Source for unit_sphere.stl
// Compile with: openscad -o unit_sphere.stl unit_sphere.scad

// Note that the 0.01 here means that we allow at most a 1x10^-2 error in
// position.
sphere($fs=0.01, r=1);
