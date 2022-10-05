linear_extrude() {
    square(size=[1, 1], center=true);
};

linear_extrude(height=40, twist=180) {
    square(size=[2, 8], center=true);
};

translate([0, 0, 50]) {
    linear_extrude(height=15, center=true, scale=2) {
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
