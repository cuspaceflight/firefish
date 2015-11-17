domain_length = 2; // metres
domain_width = 1; // metres

// Load in the rocket CAD model. This becomes surface loop "1".
Merge "cartoon-rocket.meshed.surface.stl";
Surface Loop (1) = {1};

// Now create domain
Point(1) = { -0.5 * domain_width, -0.5 * domain_width, -0.5 * domain_length };
domain_lines[] = Extrude { domain_width, 0, 0 } { Point{1}; };
domain_surfaces[] = Extrude { 0, domain_width, 0 } { Line{domain_lines[1]}; };
domain_boundary[] = Extrude { 0, 0, domain_length } { Surface{domain_surfaces[1]}; };

Delete { Volume{domain_boundary[1]}; }
domain_boundary -= domain_boundary[1];
domain_boundary += domain_surfaces[1];
Surface Loop (2) = { domain_boundary[] };

Physical Surface ("body") = {1};
Physical Surface ("domain") = { domain_boundary[] };

Volume(1) = {2, -1};
Physical Volume ("internal") = {1};
