module module2() {
    rotate(a=45.0) {
        children();
    };
};

module2() {
    square(size=[1, 3], center=true);
};
