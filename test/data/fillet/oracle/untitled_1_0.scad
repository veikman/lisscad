union() {
    union() {
        linear_extrude(height=5.166666666666667) {
            difference() {
                offset(r=0) {
                    circle(r=10);
                };
                offset(r=-0.06993351408365323) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=4.333333333333333) {
            difference() {
                offset(r=-0.06993351408365323) {
                    circle(r=10);
                };
                offset(r=-0.2859547920896832) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=3.5) {
            difference() {
                offset(r=-0.2859547920896832) {
                    circle(r=10);
                };
                offset(r=-0.669872981077807) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=2.6666666666666665) {
            difference() {
                offset(r=-0.669872981077807) {
                    circle(r=10);
                };
                offset(r=-1.2732200375003506) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=1.833333333333333) {
            difference() {
                offset(r=-1.2732200375003506) {
                    circle(r=10);
                };
                offset(r=-2.236146008037167) {
                    circle(r=10);
                };
            };
        };
        linear_extrude(height=1) {
            difference() {
                offset(r=-2.236146008037167) {
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
