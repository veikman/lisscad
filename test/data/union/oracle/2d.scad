union() {
    translate(v=[0, 4]) {
        square(size=[1, 2], center=true);
    };
    hull() {
        square(size=[2, 1], center=true);
        translate(v=[4, -4]) {
            square(size=[2, 1], center=true);
        };
    };
};
