difference() {
    polyhedron(points=[[0, 0, 0], [7, 0, 0], [7, 5, 0], [0, 5, 0], [0, 5, 4], [7, 5, 4]], faces=[[0, 1, 2, 3], [5, 4, 3, 2], [0, 4, 5, 1], [0, 3, 4], [5, 2, 1]]);
    // This is here just to provide the validity of the polyhedron:
    translate([0, 5, 0]) {
        cube(size=[4, 4, 10], center=true);
    };
};
