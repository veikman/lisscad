union() {
    sphere(r=4);
    translate(v=[5, 0, 0]) {
        resize(newsize=[4, 4, 8]) {
            sphere(r=4);
        };
    };
};
