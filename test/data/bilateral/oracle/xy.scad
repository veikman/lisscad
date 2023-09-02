union() {
    union() {
        translate(v=[6, 2]) {
            rotate(a=34.37746770784939) {
                square(size=[10, 5], center=true);
            };
        };
        mirror(v=[1, 0, 0]) {
            translate(v=[6, 2]) {
                rotate(a=34.37746770784939) {
                    square(size=[10, 5], center=true);
                };
            };
        };
    };
    mirror(v=[0, 1, 0]) {
        union() {
            translate(v=[6, 2]) {
                rotate(a=34.37746770784939) {
                    square(size=[10, 5], center=true);
                };
            };
            mirror(v=[1, 0, 0]) {
                translate(v=[6, 2]) {
                    rotate(a=34.37746770784939) {
                        square(size=[10, 5], center=true);
                    };
                };
            };
        };
    };
};
