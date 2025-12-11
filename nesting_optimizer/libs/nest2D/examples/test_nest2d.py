import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# use TKAgg backend for better compatibility
matplotlib.use('TkAgg')

try:
    from nest2D import Point, Box, Item, nest, SVGWriter, PlacerType, SelectorType
except ImportError as e :
    print("Error importing nest2D module. Make sure the nest2D library is installed and accessible.")
    raise e

MM = 1000000

def calculate_polygon_area(points):
    """Calculate area of polygon using shoelace formula"""
    n = len(points)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0

def get_bounding_box_area(points):
    """Get area of axis-aligned bounding box around points"""
    if not points:
        return 0.0

    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]

    width = max(x_coords) - min(x_coords)
    height = max(y_coords) - min(y_coords)

    return width * height

def simple_convex_hull(points):
    """
    Simple convex hull implementation using Gift wrapping algorithm
    Returns indices of points that form the convex hull
    """
    if len(points) < 3:
        return list(range(len(points)))

    # Convert points to numpy array for easier computation
    points = np.array(points)
    n = len(points)

    # Find the leftmost point
    leftmost = 0
    for i in range(1, n):
        if points[i][0] < points[leftmost][0]:
            leftmost = i
        elif points[i][0] == points[leftmost][0] and points[i][1] < points[leftmost][1]:
            leftmost = i

    hull = []
    p = leftmost

    while True:
        hull.append(p)

        # Find the next point that makes the largest left turn
        q = (p + 1) % n
        for i in range(n):
            if i == p:
                continue

            # Calculate cross product to determine turn direction
            cross = ((points[i][0] - points[p][0]) * (points[q][1] - points[p][1]) -
                    (points[i][1] - points[p][1]) * (points[q][0] - points[p][0]))

            if cross > 0 or (cross == 0 and
                           ((points[i][0] - points[p][0])**2 + (points[i][1] - points[p][1])**2) >
                           ((points[q][0] - points[p][0])**2 + (points[q][1] - points[p][1])**2)):
                q = i

        p = q
        if p == leftmost:
            break

    return hull

def trace_cutting_boundary(shape_points_list, cutting_tolerance=3.0):
    """
    Trace the actual cutting boundary by finding the outer perimeter of all shapes
    """
    if not shape_points_list:
        return []

    # Collect all points from all shapes
    all_points = []
    for shape_points in shape_points_list:
        all_points.extend(shape_points)

    if len(all_points) < 3:
        return []

    # Find the convex hull of all points (this gives us the outer boundary)
    hull_indices = simple_convex_hull(all_points)
    hull_points = [all_points[i] for i in hull_indices]

    # Expand the hull outward by cutting tolerance
    expanded_boundary = expand_cutting_path(hull_points, cutting_tolerance)

    return expanded_boundary

def find_boundary_edges(all_edges, tolerance, shape_points_list):
    """
    Simplified boundary edge detection - find edges that are on the outer perimeter
    """
    boundary_edges = []

    # For each edge, check if it's on the outer boundary by seeing if there's
    # material (other shapes) on both sides
    for edge in all_edges:
        p1, p2 = edge

        # Get the midpoint of the edge
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2

        # Calculate the normal vector (perpendicular to edge)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = (dx*dx + dy*dy) ** 0.5

        if length > 0:
            # Two normal directions (left and right of edge)
            nx1 = -dy / length * tolerance
            ny1 = dx / length * tolerance
            nx2 = dy / length * tolerance
            ny2 = -dx / length * tolerance

            # Test points on both sides of the edge
            test1 = [mid_x + nx1, mid_y + ny1]
            test2 = [mid_x + nx2, mid_y + ny2]

            # Count how many shapes contain each test point
            inside1 = sum(1 for shape in shape_points_list if is_point_inside_polygon(test1, shape))
            inside2 = sum(1 for shape in shape_points_list if is_point_inside_polygon(test2, shape))

            # If one side has no shapes (is outside), this is a boundary edge
            if inside1 == 0 or inside2 == 0:
                boundary_edges.append(edge)

    return boundary_edges

def connect_boundary_edges(boundary_edges, tolerance):
    """
    Connect boundary edges into a continuous cutting path
    """
    if not boundary_edges:
        return []

    # Start with the leftmost edge
    if not boundary_edges:
        return []

    # Find starting edge (leftmost point)
    start_edge = min(boundary_edges, key=lambda e: min(e[0][0], e[1][0]))

    cutting_path = []
    current_edge = start_edge
    used_edges = set()

    while current_edge and current_edge not in used_edges:
        used_edges.add(current_edge)

        # Add points from current edge
        if not cutting_path:
            cutting_path.append(current_edge[0])
        cutting_path.append(current_edge[1])

        # Find next connected edge
        next_edge = None
        min_distance = float('inf')

        for edge in boundary_edges:
            if edge in used_edges:
                continue

            # Check if this edge connects to current edge end
            p1, p2 = edge
            current_end = current_edge[1]

            dist1 = ((p1[0] - current_end[0])**2 + (p1[1] - current_end[1])**2) ** 0.5
            dist2 = ((p2[0] - current_end[0])**2 + (p2[1] - current_end[1])**2) ** 0.5

            if dist1 < tolerance and dist1 < min_distance:
                next_edge = edge
                min_distance = dist1
            elif dist2 < tolerance and dist2 < min_distance:
                next_edge = (p2, p1)  # Reverse edge direction
                min_distance = dist2

        # If no connected edge found, try to bridge gaps
        if not next_edge and cutting_path:
            break

        current_edge = next_edge

    # If we have a path, expand it outward by cutting tolerance
    if len(cutting_path) >= 3:
        expanded_path = expand_cutting_path(cutting_path, tolerance)
        return expanded_path

    # Fallback to convex hull if path tracing fails
    if cutting_path:
        hull_indices = simple_convex_hull(cutting_path)
        return [cutting_path[i] for i in hull_indices]

    return []

def expand_cutting_path(path_points, tolerance):
    """
    Expand the cutting path outward by the cutting tolerance using centroid-based expansion
    """
    if len(path_points) < 3:
        return path_points

    # Find centroid of the polygon
    cx = sum(p[0] for p in path_points) / len(path_points)
    cy = sum(p[1] for p in path_points) / len(path_points)

    expanded_path = []
    for point in path_points:
        x, y = point

        # Vector from centroid to point
        dx = x - cx
        dy = y - cy

        # Normalize and extend by tolerance
        length = (dx*dx + dy*dy) ** 0.5
        if length > 0:
            # Extend outward by tolerance
            factor = (length + tolerance) / length
            expanded_x = cx + dx * factor
            expanded_y = cy + dy * factor
            expanded_path.append([expanded_x, expanded_y])
        else:
            expanded_path.append([x, y])

    return expanded_path

def find_cutting_boundary(all_points, sheet_w, sheet_h):
    """
    Find the cutting boundary using convex hull with proper expansion
    """
    if len(all_points) < 3:
        return []

    # Get convex hull of all points
    hull_indices = simple_convex_hull(all_points)
    hull_points = [all_points[i] for i in hull_indices]

    # Expand outward by cutting tolerance
    cutting_tolerance = 4.0  # mm - sufficient clearance for cutting
    expanded_hull = expand_cutting_path(hull_points, cutting_tolerance)

    return expanded_hull

def calculate_cutting_waste(shape_points_list, cutting_boundary_points):
    """
    Calculate waste as area inside cutting boundary but outside actual shapes
    """
    if not cutting_boundary_points:
        return 0.0, 0.0, 0.0

    # Calculate cutting area
    cutting_area = calculate_polygon_area(cutting_boundary_points)

    # Calculate total shape area
    total_shape_area = 0.0
    for shape_points in shape_points_list:
        total_shape_area += calculate_polygon_area(shape_points)

    # Waste = cutting area - actual shapes
    waste_area = cutting_area - total_shape_area

    return max(0.0, waste_area), cutting_area, total_shape_area

def is_point_inside_polygon(point, polygon):
    """
    Check if a point is inside a polygon using ray casting algorithm
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
                    elif p1x == p2x:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def get_waste_polygons(shape_points_list, cutting_boundary_points, resolution=5):
    """
    Find waste areas by creating a grid inside cutting boundary and excluding shape areas
    Returns list of waste area polygons
    """
    if not cutting_boundary_points:
        return []

    # Get bounding box of cutting area
    x_coords = [p[0] for p in cutting_boundary_points]
    y_coords = [p[1] for p in cutting_boundary_points]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    waste_points = []

    # Create grid and find points inside cutting boundary but outside shapes
    for x in np.arange(x_min, x_max, resolution):
        for y in np.arange(y_min, y_max, resolution):
            point = [x, y]

            # Check if point is inside cutting boundary
            if is_point_inside_polygon(point, cutting_boundary_points):
                # Check if point is NOT inside any shape
                inside_shape = False
                for shape_points in shape_points_list:
                    if is_point_inside_polygon(point, shape_points):
                        inside_shape = True
                        break

                if not inside_shape:
                    waste_points.append(point)

    return waste_points

def calculate_waste_analysis(pgrp, box):
    """
    Calculate comprehensive waste analysis for nested items

    Returns:
    - sheet_area: Total sheet area
    - total_shape_area: Sum of all actual shape areas
    - cutting_waste_bbox: Waste using bounding box method
    - cutting_waste_hull: Waste using convex hull method
    - material_efficiency: Percentage of material actually used
    """

    # Calculate box dimensions manually since width()/height() methods aren't exposed
    # Box is created with Box(width, height) so we can get dimensions from the constructor values
    # For now, we'll need to pass the dimensions separately or calculate from the global sheet size
    # Let's use a simple approach by getting the sheet dimensions from the calling function

    # Temporary solution: We'll modify this to accept sheet dimensions
    return calculate_waste_analysis_with_dims(pgrp, box, 1000, 1000)  # Default dimensions

def calculate_waste_analysis_with_dims(pgrp, box, sheet_w, sheet_h):
    """
    Calculate waste analysis using reliable convex hull boundary detection
    """
    sheet_area = sheet_w * sheet_h
    total_shape_area = 0.0
    total_cutting_area = 0.0
    total_waste_area = 0.0

    print(f"\nReliable Cutting Boundary Waste Analysis:")
    print(f"Sheet size: {sheet_w:.1f} x {sheet_h:.1f} mm")
    print(f"Total sheet area: {sheet_area:.2f} mm²")
    print("-" * 50)

    bin_count = 0
    for bin_items in pgrp:
        bin_count += 1
        print(f"\nBin {bin_count} - {len(bin_items)} items:")

        # Collect individual shapes and all points
        all_bin_points = []
        bin_shape_points_list = []

        for item_idx, item in enumerate(bin_items):
            vertices = item.get_vertices()
            points = [(pt.x / MM, pt.y / MM) for pt in vertices]

            shape_area = calculate_polygon_area(points)
            print(f"  Item {item_idx + 1}: {shape_area:.2f} mm²")

            all_bin_points.extend(points)
            bin_shape_points_list.append(points)

        # Use reliable boundary detection
        cutting_boundary = None
        if all_bin_points:
            # Use convex hull approach which is more reliable
            cutting_boundary = find_cutting_boundary(all_bin_points, sheet_w, sheet_h)

        if cutting_boundary:
            bin_waste_area, bin_cutting_area, bin_shape_area = calculate_cutting_waste(
                bin_shape_points_list, cutting_boundary)

            print(f"  Total shapes area: {bin_shape_area:.2f} mm²")
            print(f"  Cutting area: {bin_cutting_area:.2f} mm²")
            print(f"  Waste area: {bin_waste_area:.2f} mm²")
            if bin_cutting_area > 0:
                cutting_efficiency = (bin_shape_area / bin_cutting_area) * 100
                waste_percentage = (bin_waste_area / bin_cutting_area) * 100
                print(f"  Cutting efficiency: {cutting_efficiency:.1f}%")
                print(f"  Waste percentage: {waste_percentage:.1f}%")

            total_shape_area += bin_shape_area
            total_cutting_area += bin_cutting_area
            total_waste_area += bin_waste_area

    # Calculate overall efficiency
    material_efficiency = (total_shape_area / sheet_area) * 100
    cutting_efficiency = (total_shape_area / total_cutting_area) * 100 if total_cutting_area > 0 else 0
    sheet_unused = sheet_area - total_cutting_area

    print(f"\n" + "=" * 50)
    print(f"CUTTING BOUNDARY ANALYSIS RESULTS:")
    print(f"Total shape area: {total_shape_area:.2f} mm²")
    print(f"Total cutting area: {total_cutting_area:.2f} mm²")
    print(f"True waste area: {total_waste_area:.2f} mm²")
    print(f"Sheet unused area: {sheet_unused:.2f} mm²")
    print(f"")
    print(f"Material efficiency: {material_efficiency:.1f}% (shapes/sheet)")
    print(f"Cutting efficiency: {cutting_efficiency:.1f}% (shapes/cutting)")
    print(f"Waste percentage: {(total_waste_area/total_cutting_area)*100:.1f}% (waste/cutting)")

    return {
        'sheet_area': sheet_area,
        'total_shape_area': total_shape_area,
        'total_cutting_area': total_cutting_area,
        'total_waste_area': total_waste_area,
        'sheet_unused': sheet_unused,
        'material_efficiency': material_efficiency,
        'cutting_efficiency': cutting_efficiency
    }

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
    for i in range(n):
        # triangle shape 95 * 68 * 68
        item = Item([
            Point(-47500000, 32660000),
            Point(47500000, 32660000),
            Point(47500000, -2 * 32660000),
            Point(-47500000, 32660000)
        ])
        shapes.append(item)

def test_1():
    sheet_w = 420
    sheet_h = 420
    box = Box(sheet_w * MM, sheet_h * MM)

    shapes = []
    add_triangle_shape(4, shapes)
    # add_rect_shape(4, shapes)

    pgrp = nest(shapes, box,
                placer_type=PlacerType.NFP,
                selector_type=SelectorType.DJDHeuristic,
                spacing=0.0)

    # Print reliable waste calculation results
    # waste_data = calculate_waste_analysis_with_dims(pgrp, box, sheet_w, sheet_h)

    # Single plot with blue shapes and red waste areas
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.set_aspect('equal')
    ax.add_patch(patches.Rectangle((0, 0), sheet_w, sheet_h, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3))

    for bin_items in pgrp:
        all_points = []

        # Collect all shape points
        for item in bin_items:
            vertices = item.get_vertices()
            points = [(pt.x / MM, pt.y / MM) for pt in vertices]
            all_points.extend(points)

        # Find cutting boundary using reliable convex hull approach
        # if len(all_points) >= 3:
        #     cutting_boundary = find_cutting_boundary(all_points, sheet_w, sheet_h)
        #
        #     if cutting_boundary:
        #         # Draw cutting boundary as red dashed line
        #         boundary_polygon = patches.Polygon(cutting_boundary, closed=True, fill=False,
        #                                          edgecolor='red', linewidth=2, linestyle='--', alpha=0.8)
        #         ax.add_patch(boundary_polygon)
        #
        #         # Fill entire cutting area with light red (waste area)
        #         waste_fill = patches.Polygon(cutting_boundary, closed=True, fill=True,
        #                                    facecolor='red', alpha=0.2, edgecolor='none')
        #         ax.add_patch(waste_fill)

        # Draw blue shapes ON TOP of waste areas (so actual shapes are not red)
        for item in bin_items:
            vertices = item.get_vertices()
            points = [(pt.x / MM, pt.y / MM) for pt in vertices]

            shape_polygon = patches.Polygon(points, closed=True, fill=True,
                                          facecolor='blue', edgecolor='black', alpha=0.8, linewidth=1)
            ax.add_patch(shape_polygon)

    # ax.set_title(f'Cutting Boundary Analysis - Efficiency: {waste_data["cutting_efficiency"]:.1f}%')
    ax.grid(True, alpha=0.3)

    # Add legend
    # from matplotlib.lines import Line2D
    legend_elements = [
        patches.Patch(facecolor='blue', alpha=0.8, label='Actual Shapes'),
        # patches.Patch(facecolor='red', alpha=0.2, label='Waste Areas'),
        # Line2D([0], [0], color='red', linewidth=2, linestyle='--', label='Cutting Boundary')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.show()


if __name__ == '__main__':
    test_1()
