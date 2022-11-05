union() {
    sphere(r=2);
    translate(v=[5, 0, 0]) {
        resize(newsize=[2, 2, 4]) {
            sphere(r=4);
        };
    };
};
