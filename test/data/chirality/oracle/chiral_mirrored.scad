module screw() {
    mirror(v=[1, 0, 0]) {
        rotate(a=[11.459155902616464, 0, 11.459155902616464]) {
            cube(size=[0.7, 0.7, 5], center=true);
        };
    };
};

module sprocket() {
    sphere(r=1);
};

mirror(v=[1, 0, 0]) {
    difference() {
        union() {
            translate(v=[0, 0, 2]) {
                cube(size=[2, 1, 5], center=true);
            };
            translate(v=[2, 0, 0]) {
                cube(size=[5, 2, 1], center=true);
            };
            translate(v=[0, 2, 0]) {
                cube(size=[1, 5, 2], center=true);
            };
        };
        translate(v=[3, 0, 0]) {
            screw() {};
        };
        translate(v=[0, 0, 3]) {
            sprocket() {};
        };
    };
};
