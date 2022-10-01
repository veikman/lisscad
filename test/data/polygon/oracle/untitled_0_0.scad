polygon(points=[[0, 0], [0, 9], [9, 9], [5, 0]]);

translate([-10, 0]) {
    polygon(points=[[0, 0], [0, 9], [9, 9], [5, 0]], paths=[[0, 2, 1, 3]]);
};

translate([0, -10]) {
    polygon(points=[[0, 0], [0, 9], [9, 9], [5, 0], [1, 1], [1, 8], [4, 8]], paths=[[0, 1, 2, 3], [4, 5, 6]], convexity=2);
};
