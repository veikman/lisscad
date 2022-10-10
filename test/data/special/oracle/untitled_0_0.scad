$fn = 3;

translate(v=[20, 0, 0]) {
    cylinder(r=10, h=20, center=true);
};

union() {
    $fn = $preview ? 4 : 5;
    cylinder(r=10, h=20, center=true);
};
