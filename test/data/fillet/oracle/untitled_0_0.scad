union() {
    union() {
        linear_extrude(height=5.166666666666667) {
            offset(r=0.06993351408365323) {
                circle(r=10);
            };
        };
        linear_extrude(height=4.333333333333333) {
            offset(r=0.2859547920896832) {
                circle(r=10);
            };
        };
        linear_extrude(height=3.5) {
            offset(r=0.669872981077807) {
                circle(r=10);
            };
        };
        linear_extrude(height=2.6666666666666665) {
            offset(r=1.2732200375003506) {
                circle(r=10);
            };
        };
        linear_extrude(height=1.833333333333333) {
            offset(r=2.236146008037167) {
                circle(r=10);
            };
        };
        linear_extrude(height=1) {
            offset(r=5) {
                circle(r=10);
            };
        };
    };
    %translate(v=[0, 0, 5]) {
        cylinder(r=10, h=10, center=true);
    };
};
