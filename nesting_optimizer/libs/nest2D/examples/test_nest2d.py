import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# use TKAgg backend for better compatibility
matplotlib.use('TkAgg')

try:
    from nest2D import Point, Box, Item, nest, SVGWriter
except ImportError as e :
    print("Error importing nest2D module. Make sure the nest2D library is installed and accessible.")
    raise e

MM = 1000000

def add_rect_shape(n, shapes):
    for i in range(n):
        # rectangle shape 100 * 100
        item = Item([
            Point(-50000000, 50000000),
            Point(50000000, 50000000),
            Point(50000000, -50000000),
            Point(-50000000, -50000000),
            Point(-50000000, 50000000)
        ])
        shapes.append(item)

def add_triangle_shape(n, shapes):
    import math
    side = 100 * MM
    height = int(math.sqrt(3)/2 * side)  # convert to int
    for i in range(n):
        item = Item([
            Point(int(-side/2), height//2),
            Point(int(side/2), height//2),
            Point(0, -height//2),
            Point(int(-side/2), height//2)  # close the polygon
        ])
        shapes.append(item)

def test_1():
    sheet_w = 1000
    sheet_h = 1000
    box = Box(sheet_w * MM, sheet_h * MM)

    shapes = []

    # add_triangle_shape(21, shapes)

    # add_rect_shape(9, shapes)

    pgrp = nest(shapes, box)

    # Visualization using matplotlib
    fig, ax = plt.subplots(figsize=(sheet_w/25.4, sheet_h/25.4), dpi=100)
    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.set_aspect('equal')
    ax.add_patch(patches.Rectangle((0, 0), sheet_w, sheet_h, linewidth=1, edgecolor='black', facecolor='none'))

    for bin_items in pgrp:  # iterate over bins
        for item in bin_items:  # iterate over items in bin
            points = [(pt.x / MM, pt.y / MM) for pt in item.get_vertices()]
            polygon = patches.Polygon(points, closed=True, fill=True, edgecolor='blue', alpha=0.5)
            ax.add_patch(polygon)

    plt.title('Nesting Result')
    plt.xlabel('Width (mm)')
    plt.ylabel('Height (mm)')
    plt.grid(True)
    plt.show()



if __name__ == '__main__':
    test_1()
