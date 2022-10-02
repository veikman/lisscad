linear_extrude(center=true) {
    square(size=[2, 8], center=true);
};

linear_extrude(height=80, center=true, twist=180) {
    square(size=[2, 8], center=true);
};

translate([0, 0, 55]) {
    linear_extrude(height=20, scale=2) {
        square(size=[2, 8], center=true);
    };
};

rotate_extrude() {
    translate([36, 0]) {
        square(size=[2, 8], center=true);
    };
};

rotate_extrude(angle=315) {
    translate([40, 0]) {
        square(size=[2, 8], center=true);
    };
};
