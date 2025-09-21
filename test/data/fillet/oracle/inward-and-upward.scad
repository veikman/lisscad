union() {
    union() {
        linear_extrude(height=5) {
            difference() {
                offset(r=0) {
                    circle(r=10);
                };
                offset(r=-0.10102051443364402) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=4) {
            difference() {
                offset(r=-0.10102051443364402) {
                    circle(r=10);
                };
                offset(r=-0.41742430504416006) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=3) {
            difference() {
                offset(r=-0.41742430504416006) {
                    circle(r=10);
                };
                offset(r=-0.9999999999999998) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=2) {
            difference() {
                offset(r=-0.9999999999999998) {
                    circle(r=10);
                };
                offset(r=-2.000000000000001) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=1) {
            difference() {
                offset(r=-2.000000000000001) {
                    circle(r=10);
                };
                offset(r=-5) {
                    circle(r=10);
                };
            };
        };
    };
    %difference() {
        translate(v=[0, 0, 2.5]) {
            cube(size=[25, 25, 5], center=true);
        };
        cylinder(r=10, h=20, center=true);
    };
};
