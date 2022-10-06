projection() {
    rotate(a=[34.37746770784939, 0, 0]) {
        cylinder(r1=6.4, r2=3.2, h=50, center=true);
    };
};

projection(cut=true) {
    translate(v=[10, 0, 0]) {
        rotate(a=[34.37746770784939, 0, 0]) {
            cylinder(r1=6.4, r2=3.2, h=50, center=true);
        };
    };
};
