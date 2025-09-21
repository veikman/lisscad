union() {
    union() {
        translate(v=[0, 0, -5]) {
            linear_extrude(height=5) {
                offset(r=0.10102051443364402) {
                    circle(r=10);
                };
            };
        };
        translate(v=[0, 0, -4]) {
            linear_extrude(height=4) {
                offset(r=0.41742430504416006) {
                    circle(r=10);
                };
            };
        };
        translate(v=[0, 0, -3]) {
            linear_extrude(height=3) {
                offset(r=0.9999999999999998) {
                    circle(r=10);
                };
            };
        };
        translate(v=[0, 0, -2]) {
            linear_extrude(height=2) {
                offset(r=2.000000000000001) {
                    circle(r=10);
                };
            };
        };
        translate(v=[0, 0, -1]) {
            linear_extrude(height=1) {
                offset(r=5) {
                    circle(r=10);
                };
            };
        };
    };
    %translate(v=[0, 0, -5]) {
        cylinder(r=10, h=10, center=true);
    };
};
