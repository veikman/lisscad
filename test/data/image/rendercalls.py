[
    ['openscad', '-o', 'mockrender/pa.stl', 'fixture/pa.scad'],
    ['openscad', '-o', 'mockrender/papa.png', 'fixture/pa.scad'],
    ['openscad', '-o', 'mockrender/re.stl', 'fixture/re.scad'],
    [
        'openscad',
        '-o',
        'mockrender/repa.png',
        '--camera',
        '100.0,100.0,20.0,0.0,0.0,0.0',
        'fixture/re.scad',
    ],
    [
        'openscad',
        '-o',
        'mockrender/rere.png',
        '--camera',
        '0.0,0.0,0.0,-10.0,5.0,0.0,20.0',
        'fixture/re.scad',
    ],
]
