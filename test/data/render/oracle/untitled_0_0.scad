translate(v=[-4, 0, 0]) {
    difference() {
        cylinder(r=10, h=5, center=true);
        cylinder(r=8, h=5, center=true);
    };
};

translate(v=[4, 0, 0]) {
    render() {
        difference() {
            cylinder(r=10, h=5, center=true);
            cylinder(r=8, h=5, center=true);
        };
    };
};
