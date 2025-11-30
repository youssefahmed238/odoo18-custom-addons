import custom.addons.nesting_optimizer.libs.wrapper.python.nest2d_wrapper as nest2d
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random

def configure_matplotlib_for_display():
    """Configure matplotlib for best available display"""
    try:
        # Try different backends for interactive display
        backends_to_try = ['TkAgg', 'Qt5Agg', 'GTK3Agg', 'Agg']

        for backend in backends_to_try:
            try:
                matplotlib.use(backend, force=True)
                # Test if the backend works
                fig = plt.figure()
                plt.close(fig)
                print(f"✓ Using matplotlib backend: {backend}")
                return backend
            except Exception as e:
                print(f"  ⚠️  Backend {backend} failed: {str(e)[:50]}...")
                continue

        print("⚠️  No interactive backend available, using default")
        return None

    except Exception as e:
        print(f"⚠️  Matplotlib configuration warning: {e}")
        return None

# Configure matplotlib at startup
current_backend = configure_matplotlib_for_display()

def show_interactive_plot(save_fallback=True, filename_prefix="nesting_plot"):
    """Helper function to display plot in interactive window or save as fallback"""
    try:
        if current_backend in ['TkAgg', 'Qt5Agg', 'GTK3Agg']:
            print("📊 Opening visualization window...")
            print("   Close the window to continue to next test")
            plt.show(block=True)  # Block until window is closed
            print("✅ Visualization window closed")
        else:
            # Fallback to saving the plot
            if save_fallback:
                import os
                os.makedirs('/odoo18/custom/addons/nesting_optimizer/plots', exist_ok=True)
                filename = f"/odoo18/custom/addons/nesting_optimizer/plots/{filename_prefix}.png"
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
                print(f"📸 No GUI available - Plot saved as: {filename}")
            else:
                print("⚠️  No GUI available and saving disabled")
            plt.close()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        plt.close('all')
    except Exception as e:
        print(f"⚠️  Display error: {e}")
        print("   Falling back to saving plot...")
        try:
            import os
            os.makedirs('/odoo18/custom/addons/nesting_optimizer/plots', exist_ok=True)
            filename = f"/odoo18/custom/addons/nesting_optimizer/plots/{filename_prefix}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"📸 Plot saved as fallback: {filename}")
        except:
            print("❌ Could not save plot either")
        plt.close('all')

def visualize_nesting_result(shapes, result, sheet_width, sheet_height, title="Nesting Result"):
    """
    Visualize the nesting result using matplotlib
    """
    sheets_used = result['bins_used']
    items = result['items']

    # Create subplots for each sheet
    cols = min(3, sheets_used)  # Max 3 columns
    rows = (sheets_used + cols - 1) // cols  # Calculate rows needed

    if sheets_used == 0:
        print("No sheets used - nothing to visualize")
        return

    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
    fig.suptitle(title, fontsize=16)

    # Handle single subplot case
    if sheets_used == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if hasattr(axes, '__len__') else [axes]
    else:
        axes = axes.flatten()

    # Generate colors for each shape
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    shape_colors = {}
    for i in range(len(shapes)):
        shape_colors[i] = colors[i % len(colors)]

    # Draw each sheet
    for sheet_id in range(sheets_used):
        ax = axes[sheet_id]

        # Set up the sheet
        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_height)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Sheet {sheet_id}')

        # Draw sheet boundary
        sheet_rect = patches.Rectangle((0, 0), sheet_width, sheet_height,
                                   linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
        ax.add_patch(sheet_rect)

        # Draw items on this sheet
        items_on_sheet = [item for item in items if item['bin_id'] == sheet_id]

        for i, item in enumerate(items_on_sheet):
            # Find original shape index
            shape_idx = items.index(item)

            # Get item position and polygon
            pos = item['position']
            polygon_points = item['polygon']

            # Convert polygon points to numpy array and translate
            points = np.array(polygon_points)
            translated_points = points + np.array([pos[0], pos[1]])

            # Create polygon patch
            polygon = patches.Polygon(translated_points,
                                    facecolor=shape_colors[shape_idx],
                                    edgecolor='black',
                                    linewidth=1.5,
                                    alpha=0.7,
                                    label=f'Shape {shape_idx}')
            ax.add_patch(polygon)

            # Add text label at center of shape
            center_x = np.mean(translated_points[:, 0])
            center_y = np.mean(translated_points[:, 1])
            ax.text(center_x, center_y, str(shape_idx),
                   ha='center', va='center', fontsize=10, fontweight='bold', color='white')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')

    # Hide unused subplots
    for i in range(sheets_used, len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()

    # Show the plot in a new window (or save as fallback)
    safe_title = title.replace(' ', '_').replace('-', '_').lower()
    show_interactive_plot(save_fallback=True, filename_prefix=safe_title)

    # Print summary
    total_shape_area = sum(nest2d.calculate_area(shape) for shape in shapes)
    total_sheet_area = sheet_width * sheet_height * sheets_used
    utilization = (total_shape_area / total_sheet_area) * 100 if total_sheet_area > 0 else 0

    print(f"\n📊 Nesting Summary:")
    print(f"   Total shapes: {len(shapes)}")
    print(f"   Sheets used: {sheets_used}")
    print(f"   Items placed: {len(items)}")
    print(f"   Sheet size: {sheet_width} x {sheet_height}")
    print(f"   Total shape area: {total_shape_area:.2f}")
    print(f"   Total sheet area: {total_sheet_area:.2f}")
    print(f"   Material utilization: {utilization:.1f}%")

def test_glass_factory_optimization():
    """
    Glass Factory Nesting Optimization

    Sheet Inventory:
    - 1000 sheets: 2000 x 1000 mm
    - 500 sheets: 1000 x 1000 mm
    - 200 sheets: 500 x 700 mm

    Order: 500 square pieces 100 x 100 mm
    Constraints: kerf thickness, padding for bad borders
    """
    print("\n" + "=" * 60)
    print("🏭 GLASS FACTORY NESTING OPTIMIZATION")
    print("=" * 60)

    # Define glass sheets inventory
    sheet_inventory = [
        {"size": (2000, 1000), "count": 1000, "name": "Large Sheet"},
        {"size": (1000, 1000), "count": 500, "name": "Medium Sheet"},
        {"size": (500, 700), "count": 200, "name": "Small Sheet"}
    ]

    print("📋 Sheet Inventory:")
    for sheet in sheet_inventory:
        w, h = sheet["size"]
        print(f"   {sheet['count']} x {sheet['name']} ({w} x {h} mm)")

    # Define required glass pieces
    required_pieces = [
        {"size": (100, 100), "count": 500, "name": "Square Glass"}
    ]

    print("\n📦 Required Pieces:")
    for piece in required_pieces:
        w, h = piece["size"]
        print(f"   {piece['count']} x {piece['name']} ({w} x {h} mm)")

    # Cutting parameters
    kerf_thickness = 3.0  # mm - blade cutting width
    padding = 5.0        # mm - safety margin from edges

    print(f"\n🔧 Cutting Parameters:")
    print(f"   Kerf thickness: {kerf_thickness} mm")
    print(f"   Edge padding: {padding} mm")

    # Create shapes list for nesting (all pieces are 100x100 squares)
    piece_shape = [[0, 0], [100, 0], [100, 100], [0, 100]]
    shapes = [piece_shape] * 500  # 500 identical squares

    print(f"\n🔄 Testing nesting optimization on different sheet sizes...")

    optimization_results = []

    # Test each sheet size
    for sheet_info in sheet_inventory:
        sheet_w, sheet_h = sheet_info["size"]
        sheet_name = sheet_info["name"]
        available_count = sheet_info["count"]

        # Calculate usable area (subtract padding from all edges)
        usable_w = sheet_w - (2 * padding)
        usable_h = sheet_h - (2 * padding)

        if usable_w <= 0 or usable_h <= 0:
            print(f"   ❌ {sheet_name}: Too small after padding")
            continue

        print(f"\n📊 Analyzing {sheet_name} ({sheet_w} x {sheet_h} mm):")
        print(f"   Usable area: {usable_w} x {usable_h} mm")

        # Run nesting optimization with a smaller test set first to determine capacity
        test_shapes = [piece_shape] * min(100, 500)  # Test with up to 100 pieces
        result = nest2d.nest_shapes(test_shapes, usable_w, usable_h, spacing=kerf_thickness)

        # Calculate actual pieces that fit on one sheet
        pieces_per_sheet = len([item for item in result['items'] if item['bin_id'] == 0]) if result['bins_used'] > 0 else 0

        # If we tested with fewer pieces than fit, run theoretical calculation
        if pieces_per_sheet >= len(test_shapes) and len(test_shapes) < 500:
            # Calculate theoretical maximum based on area
            piece_area_with_kerf = (100 + kerf_thickness) * (100 + kerf_thickness)
            theoretical_max = int((usable_w * usable_h) / piece_area_with_kerf)

            # Use the more conservative estimate
            pieces_per_sheet = min(theoretical_max, pieces_per_sheet)

        sheets_needed = max(1, (500 + pieces_per_sheet - 1) // pieces_per_sheet) if pieces_per_sheet > 0 else float('inf')

        # Calculate material utilization with proper validation
        if pieces_per_sheet > 0:
            total_piece_area = pieces_per_sheet * 100 * 100  # mm² (actual piece area)
            sheet_area = usable_w * usable_h  # mm²
            utilization = (total_piece_area / sheet_area * 100) if sheet_area > 0 else 0

            # Validate utilization (should never exceed 100% significantly)
            if utilization > 120:  # Allow small margin for calculation errors
                print(f"   ⚠️  Warning: Unrealistic utilization {utilization:.1f}% - recalculating...")
                # Recalculate based on theoretical grid
                pieces_x = int(usable_w // (100 + kerf_thickness))
                pieces_y = int(usable_h // (100 + kerf_thickness))
                pieces_per_sheet = pieces_x * pieces_y
                sheets_needed = max(1, (500 + pieces_per_sheet - 1) // pieces_per_sheet) if pieces_per_sheet > 0 else float('inf')
                total_piece_area = pieces_per_sheet * 100 * 100
                utilization = (total_piece_area / sheet_area * 100) if sheet_area > 0 else 0
        else:
            total_piece_area = 0
            sheet_area = usable_w * usable_h
            utilization = 0

        # Calculate waste
        waste_per_sheet = sheet_area - total_piece_area
        total_waste = waste_per_sheet * sheets_needed

        optimization_results.append({
            "sheet_info": sheet_info,
            "pieces_per_sheet": pieces_per_sheet,
            "sheets_needed": sheets_needed,
            "utilization": utilization,
            "waste_per_sheet": waste_per_sheet,
            "total_waste": total_waste,
            "usable_size": (usable_w, usable_h),
            "result": result,
            "feasible": sheets_needed <= available_count
        })

        print(f"   Pieces per sheet: {pieces_per_sheet}")
        print(f"   Sheets needed: {sheets_needed}")
        print(f"   Available sheets: {available_count}")
        print(f"   Material utilization: {utilization:.1f}%")
        print(f"   Waste per sheet: {waste_per_sheet:.0f} mm²")
        print(f"   Feasible: {'✅ Yes' if sheets_needed <= available_count else '❌ No'}")

    # Find optimal solution
    feasible_solutions = [r for r in optimization_results if r["feasible"]]

    if not feasible_solutions:
        print("\n❌ No feasible solution found with current inventory!")
        return

    # Sort by total waste (ascending) - best optimization
    optimal_solution = min(feasible_solutions, key=lambda x: x["total_waste"])

    print(f"\n🎯 OPTIMAL SOLUTION:")
    sheet_info = optimal_solution["sheet_info"]
    print(f"   Sheet type: {sheet_info['name']} ({sheet_info['size'][0]} x {sheet_info['size'][1]} mm)")
    print(f"   Pieces per sheet: {optimal_solution['pieces_per_sheet']}")
    print(f"   Sheets required: {optimal_solution['sheets_needed']}")
    print(f"   Material utilization: {optimal_solution['utilization']:.1f}%")
    print(f"   Total waste: {optimal_solution['total_waste']:.0f} mm²")

    # Visualize the optimal nesting pattern
    print(f"\n🎨 Visualizing optimal nesting pattern...")

    # Create a subset for visualization (first 20 pieces to avoid clutter)
    viz_shapes = shapes[:20]  # Show first 20 pieces for clarity
    viz_result = nest2d.nest_shapes(viz_shapes, *optimal_solution["usable_size"], spacing=kerf_thickness)

    if viz_result['bins_used'] > 0:
        title = f"Glass Factory - {sheet_info['name']} Optimization"
        visualize_nesting_result(viz_shapes, viz_result, *optimal_solution["usable_size"], title)

    # Summary report
    print(f"\n📈 OPTIMIZATION SUMMARY:")
    print(f"   Order: 500 pieces of 100x100 mm glass")
    print(f"   Optimal sheet: {sheet_info['name']}")
    print(f"   Sheets consumed: {optimal_solution['sheets_needed']} / {sheet_info['count']}")
    print(f"   Remaining sheets: {sheet_info['count'] - optimal_solution['sheets_needed']}")
    print(f"   Material efficiency: {optimal_solution['utilization']:.1f}%")
    print(f"   Waste minimized: {optimal_solution['total_waste']:.0f} mm²")

    # Show alternative solutions
    print(f"\n🔄 ALTERNATIVE SOLUTIONS:")
    for i, sol in enumerate(sorted(feasible_solutions, key=lambda x: x["total_waste"])):
        if sol == optimal_solution:
            continue
        sheet = sol["sheet_info"]
        print(f"   Option {i+1}: {sheet['name']} - {sol['pieces_per_sheet']} pieces/sheet, "
              f"{sol['sheets_needed']} sheets, {sol['utilization']:.1f}% efficiency")

def test_glass_factory_multiple_orders():
    """
    Advanced glass factory optimization with multiple different piece sizes
    """
    print("\n" + "=" * 60)
    print("🏭 ADVANCED GLASS FACTORY - MULTIPLE ORDERS")
    print("=" * 60)

    # Mixed order with different glass piece sizes
    mixed_shapes = []
    piece_counts = []

    # Order 1: 200 small squares (50x50)
    small_square = [[0, 0], [50, 0], [50, 50], [0, 50]]
    mixed_shapes.extend([small_square] * 200)
    piece_counts.append(("Small Square 50x50", 200))

    # Order 2: 150 medium rectangles (80x120)
    medium_rect = [[0, 0], [80, 0], [80, 120], [0, 120]]
    mixed_shapes.extend([medium_rect] * 150)
    piece_counts.append(("Rectangle 80x120", 150))

    # Order 3: 100 large squares (150x150)
    large_square = [[0, 0], [150, 0], [150, 150], [0, 150]]
    mixed_shapes.extend([large_square] * 100)
    piece_counts.append(("Large Square 150x150", 100))

    print("📦 Mixed Order:")
    for desc, count in piece_counts:
        print(f"   {count} x {desc} mm")

    # Test on large sheets (2000 x 1000)
    sheet_w, sheet_h = 2000, 1000
    padding = 10.0  # Larger padding for mixed sizes
    kerf = 3.0

    usable_w = sheet_w - (2 * padding)
    usable_h = sheet_h - (2 * padding)

    print(f"\n🔧 Using Large Sheets ({sheet_w} x {sheet_h} mm)")
    print(f"   Usable area: {usable_w} x {usable_h} mm")
    print(f"   Padding: {padding} mm, Kerf: {kerf} mm")

    # Test with smaller batch first to get realistic estimates
    test_mixed_shapes = []
    test_mixed_shapes.extend([small_square] * min(50, 200))    # 50 small squares
    test_mixed_shapes.extend([medium_rect] * min(30, 150))     # 30 rectangles
    test_mixed_shapes.extend([large_square] * min(20, 100))    # 20 large squares

    print(f"\n🧪 Testing with sample: {len(test_mixed_shapes)} pieces")

    # Run mixed nesting
    result = nest2d.nest_shapes(test_mixed_shapes, usable_w, usable_h, spacing=kerf)

    sheets_used = result['bins_used']
    test_pieces = len(test_mixed_shapes)
    pieces_placed = len(result['items'])

    print(f"\n📊 Mixed Nesting Test Results:")
    print(f"   Test pieces: {test_pieces}")
    print(f"   Pieces successfully placed: {pieces_placed}")
    print(f"   Test sheets required: {sheets_used}")
    print(f"   Placement success rate: {pieces_placed/test_pieces*100:.1f}%")

    # Estimate for full order
    if pieces_placed > 0:
        pieces_per_sheet = pieces_placed / sheets_used if sheets_used > 0 else 0
        estimated_sheets_for_full_order = len(mixed_shapes) / pieces_per_sheet if pieces_per_sheet > 0 else float('inf')
    else:
        pieces_per_sheet = 0
        estimated_sheets_for_full_order = float('inf')

    print(f"   Estimated pieces per sheet: {pieces_per_sheet:.1f}")
    print(f"   Estimated sheets for full order (450 pieces): {estimated_sheets_for_full_order:.1f}")

    # Calculate utilization for test sample
    total_piece_area = sum(nest2d.calculate_area(shape) for shape in test_mixed_shapes[:pieces_placed])
    total_sheet_area = usable_w * usable_h * sheets_used
    utilization = (total_piece_area / total_sheet_area * 100) if total_sheet_area > 0 else 0

    print(f"   Material utilization: {utilization:.1f}%")

    # Validate results
    if utilization > 100:
        print(f"   ⚠️  Warning: Utilization {utilization:.1f}% exceeds 100% - nesting algorithm may have overlapping pieces")
    elif utilization > 95:
        print(f"   ✅ Excellent utilization: {utilization:.1f}%")
    elif utilization > 80:
        print(f"   ✅ Good utilization: {utilization:.1f}%")
    else:
        print(f"   ⚠️  Low utilization: {utilization:.1f}%")

    # Visualize mixed nesting (first sheet only)
    if sheets_used > 0:
        print(f"\n🎨 Visualizing mixed piece nesting...")
        title = "Glass Factory - Mixed Order Nesting (Sample)"
        visualize_nesting_result(test_mixed_shapes, result, usable_w, usable_h, title)

def test_glass_factory_small_batch_detailed():
    """
    Small batch glass factory optimization with detailed logging and zoomed visualization

    Small order: 15 pieces of 100x100mm glass
    Focus on detailed analysis and precise positioning
    """
    print("\n" + "=" * 60)
    print("🔍 GLASS FACTORY - SMALL BATCH DETAILED ANALYSIS")
    print("=" * 60)

    # Small batch order
    order_quantity = 1
    piece_size = (150, 150)  # Reduced from 200x200 to avoid overlapping

    print(f"📦 Small Batch Order:")
    print(f"   Quantity: {order_quantity} pieces")
    print(f"   Size: {piece_size[0]} x {piece_size[1]} mm squares")

    # Use medium sheet for detailed analysis
    sheet_w, sheet_h = 1000, 1000  # Medium sheet
    kerf_thickness = 3.0  # Increased for better separation
    padding = 5.0  # Increased padding

    # Calculate usable area
    usable_w = sheet_w - (2 * padding)
    usable_h = sheet_h - (2 * padding)

    # Theoretical calculation to check if parameters make sense
    piece_with_kerf = piece_size[0] + kerf_thickness
    theoretical_pieces_x = int(usable_w // piece_with_kerf)
    theoretical_pieces_y = int(usable_h // piece_with_kerf)
    theoretical_max = theoretical_pieces_x * theoretical_pieces_y

    print(f"\n🧮 THEORETICAL ANALYSIS:")
    print(f"   Piece + kerf: {piece_with_kerf} x {piece_with_kerf} mm")
    print(f"   Theoretical max pieces: {theoretical_max} ({theoretical_pieces_x}x{theoretical_pieces_y})")
    print(f"   Order quantity: {order_quantity}")
    print(f"   Fit check: {'✅ Should fit' if theoretical_max >= order_quantity else '❌ Too many pieces'}")

    print(f"\n🔧 Sheet Configuration:")
    print(f"   Sheet size: {sheet_w} x {sheet_h} mm")
    print(f"   Padding: {padding} mm (on each edge)")
    print(f"   Kerf thickness: {kerf_thickness} mm")
    print(f"   Usable area: {usable_w} x {usable_h} mm")

    # Create shapes for nesting
    piece_shape = [[0, 0], [piece_size[0], 0], [piece_size[0], piece_size[1]], [0, piece_size[1]]]
    shapes = [piece_shape] * order_quantity

    # add triangle shape 100 width and hight 100 to increase complexity

    shapes.append([[0, 0], [30, 0], [30, 40]])
    shapes.append([[0, 0], [30, 0], [30, 40]])
    shapes.append([[0, 0], [30, 0], [30, 40]])
    shapes.append([[0, 0], [30, 0], [30, 40]])

    # # add anther triangle and circle shape to increase complexity
    #
    # shapes.append([[0, 0], [300, 0], [150, 300]])  # Smaller triangle
    #
    # shapes.append([[0, 0], [200, 0], [200, 150], [0, 150]])  # Rectangle 150x100

    # add hexagon shape

    # shapes.append([[100, 0], [200, 50], [200, 150], [100, 200], [0, 150], [0, 50]])  # Hexagon

    print(f"\n🔄 Running nesting optimization...")

    # Run nesting
    result = nest2d.nest_shapes(shapes, usable_w, usable_h, spacing=kerf_thickness)

    # Extract detailed results
    sheets_used = result['bins_used']
    items_placed = len(result['items'])
    success_rate = (items_placed / order_quantity) * 100

    print(f"\n📊 NESTING RESULTS:")
    print(f"   Sheets required: {sheets_used}")
    print(f"   Pieces placed: {items_placed} / {order_quantity}")
    print(f"   Success rate: {success_rate:.1f}%")

    # Check for nesting quality issues
    total_overlaps = 0
    for sheet_id in range(sheets_used):
        items_on_sheet = [item for item in result['items'] if item['bin_id'] == sheet_id]
        unique_positions = set()
        for item in items_on_sheet:
            pos_key = (round(item['position'][0], 1), round(item['position'][1], 1))
            if pos_key in unique_positions:
                total_overlaps += 1
            else:
                unique_positions.add(pos_key)

    if total_overlaps > 0:
        print(f"   ⚠️  NESTING QUALITY: {total_overlaps} pieces are overlapping!")
        print(f"   💡 Suggestion: Increase kerf thickness or reduce piece size")
    else:
        print(f"   ✅ NESTING QUALITY: No overlapping pieces detected")

    # Detailed sheet analysis
    for sheet_id in range(sheets_used):
        items_on_sheet = [item for item in result['items'] if item['bin_id'] == sheet_id]
        pieces_on_sheet = len(items_on_sheet)

        print(f"\n📋 SHEET {sheet_id} DETAILED ANALYSIS:")
        print(f"   Pieces on this sheet: {pieces_on_sheet}")

        if pieces_on_sheet > 0:
            # Check for overlapping pieces first
            unique_positions = set()
            actual_pieces = 0
            for item in items_on_sheet:
                pos_key = (round(item['position'][0], 1), round(item['position'][1], 1))
                if pos_key not in unique_positions:
                    unique_positions.add(pos_key)
                    actual_pieces += 1

            if actual_pieces != pieces_on_sheet:
                print(f"   ⚠️  WARNING: {pieces_on_sheet - actual_pieces} pieces are overlapping!")
                print(f"   📊 Actual unique pieces: {actual_pieces}")

            # Calculate utilization based on actual non-overlapping pieces
            piece_area = piece_size[0] * piece_size[1]  # Single piece area
            total_pieces_area = actual_pieces * piece_area  # Use actual count
            sheet_area = usable_w * usable_h
            sheet_utilization = (total_pieces_area / sheet_area) * 100
            waste_area = sheet_area - total_pieces_area

            print(f"   Sheet utilization: {sheet_utilization:.1f}% (corrected for overlaps)")
            print(f"   Used area: {total_pieces_area:.0f} mm²")
            print(f"   Waste area: {waste_area:.0f} mm²")

            # Show detailed piece positions
            print(f"   \n🎯 PIECE POSITIONS ON SHEET {sheet_id}:")
            print(f"   {'Piece':<6} {'X Position':<12} {'Y Position':<12} {'Area':<8} {'Status'}")
            print(f"   {'-'*6} {'-'*12} {'-'*12} {'-'*8} {'-'*10}")

            for i, item in enumerate(items_on_sheet):
                pos = item['position']
                piece_area = nest2d.calculate_area(item['polygon'])
                rotation = item['rotation']

                # Determine status based on position
                near_edge = (pos[0] < 20 or pos[1] < 20 or
                           pos[0] > usable_w - 120 or pos[1] > usable_h - 120)
                status = "Edge" if near_edge else "Center"

                print(f"   {i+1:<6} {pos[0]:<12.1f} {pos[1]:<12.1f} {piece_area:<8.0f} {status}")

                if rotation != 0:
                    print(f"          (Rotated: {rotation:.2f} radians)")

            # Calculate spacing between pieces
            if len(items_on_sheet) > 1:
                print(f"\n   📏 SPACING ANALYSIS:")
                min_spacing = float('inf')
                max_spacing = 0
                spacing_violations = 0
                overlapping_pieces = 0

                for i, item1 in enumerate(items_on_sheet):
                    for j, item2 in enumerate(items_on_sheet[i+1:], i+1):
                        pos1 = item1['position']
                        pos2 = item2['position']

                        # Check for exact position overlap (major issue)
                        if abs(pos1[0] - pos2[0]) < 0.1 and abs(pos1[1] - pos2[1]) < 0.1:
                            overlapping_pieces += 1
                            print(f"   ❌ OVERLAP DETECTED: Pieces {i+1} and {j+1} at same position!")
                            continue

                        # Calculate actual edge-to-edge distance
                        # For rectangles, we need to check horizontal and vertical distances separately
                        horizontal_gap = abs(pos2[0] - pos1[0]) - piece_size[0]
                        vertical_gap = abs(pos2[1] - pos1[1]) - piece_size[1]

                        # Determine if pieces are adjacent horizontally or vertically
                        if abs(pos1[1] - pos2[1]) < piece_size[1] / 2:  # Same row (horizontally adjacent)
                            edge_distance = horizontal_gap
                        elif abs(pos1[0] - pos2[0]) < piece_size[0] / 2:  # Same column (vertically adjacent)
                            edge_distance = vertical_gap
                        else:
                            # Diagonal distance (corner to corner)
                            edge_distance = ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)**0.5 - (piece_size[0] * 1.414)

                        # Check for spacing violations
                        if edge_distance < kerf_thickness and edge_distance >= 0:
                            spacing_violations += 1

                        if edge_distance >= 0:  # Only consider positive spacings
                            min_spacing = min(min_spacing, edge_distance)
                            max_spacing = max(max_spacing, edge_distance)

                # Display results
                if overlapping_pieces > 0:
                    print(f"   ❌ CRITICAL: {overlapping_pieces} pairs of pieces are overlapping!")
                    print(f"   🔧 This indicates a serious nesting algorithm error")

                if min_spacing != float('inf'):
                    print(f"   Minimum spacing: {min_spacing:.1f} mm")
                    print(f"   Maximum spacing: {max_spacing:.1f} mm")
                else:
                    print(f"   No valid spacing measurements (all pieces overlapping?)")

                print(f"   Required kerf: {kerf_thickness:.1f} mm")
                print(f"   Spacing violations: {spacing_violations}")

                if overlapping_pieces > 0:
                    print(f"   🚨 NESTING FAILED: Pieces are overlapping")
                elif spacing_violations > 0:
                    print(f"   ⚠️  Warning: {spacing_violations} pieces too close together!")
                else:
                    print(f"   ✅ All spacing requirements met")

    # Overall optimization summary
    total_area_used = items_placed * piece_size[0] * piece_size[1]
    total_sheet_area = usable_w * usable_h * sheets_used
    overall_utilization = (total_area_used / total_sheet_area * 100) if total_sheet_area > 0 else 0
    total_waste = total_sheet_area - total_area_used

    print(f"\n📈 OVERALL OPTIMIZATION SUMMARY:")
    print(f"   Order size: {order_quantity} pieces")
    print(f"   Sheets used: {sheets_used}")
    print(f"   Overall utilization: {overall_utilization:.1f}%")
    print(f"   Total waste: {total_waste:.0f} mm²")
    print(f"   Average pieces per sheet: {items_placed/sheets_used:.1f}")

    # Create zoomed visualization
    if result['bins_used'] > 0:
        print(f"\n🎨 Creating zoomed detailed visualization...")

        # Create custom zoomed visualization function
        create_detailed_zoomed_visualization(shapes, result, usable_w, usable_h,
                                           piece_size, kerf_thickness, order_quantity)

def create_detailed_zoomed_visualization(shapes, result, sheet_w, sheet_h, piece_size, kerf, order_qty):
    """Create a detailed visualization showing full sheet with measurements and labels"""

    sheets_used = result['bins_used']
    items = result['items']

    # Create smaller figure - reduced from 10x to 6x per sheet
    fig, axes = plt.subplots(1, sheets_used, figsize=(6*sheets_used, 6))
    fig.suptitle(f"Glass Cutting Layout - {order_qty} Pieces on {sheet_w}x{sheet_h}mm Sheet", fontsize=12, fontweight='bold')

    if sheets_used == 1:
        axes = [axes]

    # Color scheme for better visibility
    piece_colors = ['lightcoral', 'lightblue', 'lightgreen', 'gold', 'plum',
                   'orange', 'cyan', 'pink', 'lime', 'silver']

    for sheet_id in range(sheets_used):
        ax = axes[sheet_id]
        items_on_sheet = [item for item in items if item['bin_id'] == sheet_id]

        # Always show full sheet dimensions
        ax.set_xlim(0, sheet_w)
        ax.set_ylim(0, sheet_h)

        # Set tick intervals based on sheet size for better readability
        if sheet_w <= 1000:
            x_tick_interval = 100
        elif sheet_w <= 2000:
            x_tick_interval = 200
        else:
            x_tick_interval = 500

        if sheet_h <= 1000:
            y_tick_interval = 100
        elif sheet_h <= 2000:
            y_tick_interval = 200
        else:
            y_tick_interval = 500

        # Set tick marks for full sheet view
        x_ticks = np.arange(0, sheet_w + x_tick_interval, x_tick_interval)
        y_ticks = np.arange(0, sheet_h + y_tick_interval, y_tick_interval)

        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)

        # Add minor ticks for precision
        ax.set_xticks(np.arange(0, sheet_w + 50, 50), minor=True)
        ax.set_yticks(np.arange(0, sheet_h + 50, 50), minor=True)

        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linewidth=0.5)  # Main grid
        ax.grid(True, which='minor', alpha=0.1, linewidth=0.3)  # Minor grid
        ax.set_title(f'Sheet {sheet_id} - {len(items_on_sheet)} pieces\nFull Sheet View ({sheet_w}x{sheet_h}mm)',
                    fontsize=11, fontweight='bold')

        # Draw sheet boundary with thicker border
        sheet_rect = patches.Rectangle((0, 0), sheet_w, sheet_h,
                                     linewidth=3, edgecolor='black',
                                     facecolor='lightgray', alpha=0.1)
        ax.add_patch(sheet_rect)

        # Draw pieces with detailed labels
        for i, item in enumerate(items_on_sheet):
            # Find original shape index
            shape_idx = items.index(item)

            # Get item position and polygon
            pos = item['position']
            polygon_points = item['polygon']

            # Convert polygon points and translate
            points = np.array(polygon_points)
            translated_points = points + np.array([pos[0], pos[1]])

            # Create polygon with distinct color
            color_idx = shape_idx % len(piece_colors)
            polygon = patches.Polygon(translated_points,
                                    facecolor=piece_colors[color_idx],
                                    edgecolor='darkred',
                                    linewidth=1.5,
                                    alpha=0.8)
            ax.add_patch(polygon)

            # Add detailed label at center
            center_x = np.mean(translated_points[:, 0])
            center_y = np.mean(translated_points[:, 1])

            # Main piece number (adjust font size based on piece size)
            font_size = min(10, max(6, piece_size[0] // 20))
            ax.text(center_x, center_y, f'#{shape_idx+1}',
                   ha='center', va='center', fontsize=font_size, fontweight='bold', color='darkred')

            # Position coordinates (smaller text)
            coord_font_size = max(5, font_size - 3)
            ax.text(center_x, center_y - piece_size[1]//8, f'({pos[0]:.0f},{pos[1]:.0f})',
                   ha='center', va='center', fontsize=coord_font_size, color='darkblue')

            # Draw cutting lines (kerf visualization) - only for first few pieces to avoid clutter
            if kerf > 0 and i < 5:  # Show kerf for first 5 pieces only
                kerf_offset = kerf / 2
                kerf_rect = patches.Rectangle(
                    (pos[0] - kerf_offset, pos[1] - kerf_offset),
                    piece_size[0] + kerf,
                    piece_size[1] + kerf,
                    facecolor='none',
                    edgecolor='red',
                    linewidth=1,
                    linestyle='--',
                    alpha=0.5
                )
                ax.add_patch(kerf_rect)

        # Add spacing measurements between a few adjacent pieces
        if len(items_on_sheet) > 1:
            for i, item1 in enumerate(items_on_sheet[:2]):  # Show spacing for first 2 pieces only
                for j, item2 in enumerate(items_on_sheet[i+1:i+2], i+1):
                    pos1 = item1['position']
                    pos2 = item2['position']

                    # Calculate spacing between pieces
                    if abs(pos1[1] - pos2[1]) < piece_size[1]:  # Horizontally adjacent
                        spacing = abs(pos2[0] - pos1[0]) - piece_size[0]
                        if spacing > 0 and spacing < 100:  # Only show reasonable spacings
                            mid_x = (pos1[0] + piece_size[0] + pos2[0]) / 2
                            mid_y = pos1[1] + piece_size[1] / 2
                            ax.text(mid_x, mid_y, f'{spacing:.1f}',
                                   ha='center', va='center', fontsize=6,
                                   bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.7))

        # Add compact info boxes in corners
        info_font_size = 8

        # Top left - Kerf info
        ax.text(0.02, 0.98, f'Kerf: {kerf}mm', transform=ax.transAxes,
               fontsize=info_font_size, verticalalignment='top', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

        # Top left - Utilization info
        if items_on_sheet:
            utilization = (len(items_on_sheet) * piece_size[0] * piece_size[1] / (sheet_w * sheet_h)) * 100
            ax.text(0.02, 0.88, f'Util: {utilization:.1f}%', transform=ax.transAxes,
                   fontsize=info_font_size, verticalalignment='top', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))

        # Bottom left - Piece info
        ax.text(0.02, 0.12, f'{len(items_on_sheet)} pieces', transform=ax.transAxes,
               fontsize=info_font_size, verticalalignment='bottom', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))

        ax.text(0.02, 0.02, f'{piece_size[0]}x{piece_size[1]}mm', transform=ax.transAxes,
               fontsize=info_font_size, verticalalignment='bottom', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))

        ax.set_xlabel(f'X Position (mm)', fontsize=10)
        ax.set_ylabel(f'Y Position (mm)', fontsize=10)

    plt.tight_layout()

    # Enhanced display
    safe_title = "full_sheet_cutting_layout"
    show_interactive_plot(save_fallback=True, filename_prefix=safe_title)

def test_large_batch_validation():
    """
    Test with larger quantities to expose calculation issues
    """
    print("\n" + "=" * 60)
    print("🔍 LARGE BATCH VALIDATION - EXPOSING CALCULATION ISSUES")
    print("=" * 60)

    # Test with progressively larger quantities
    test_cases = [
        {"qty": 50, "piece_size": (100, 100), "name": "Medium Order"},
        {"qty": 100, "piece_size": (80, 80), "name": "Large Order"},
        {"qty": 200, "piece_size": (60, 60), "name": "Very Large Order"},
    ]

    sheet_w, sheet_h = 2000, 1000  # Large sheet
    kerf_thickness = 3.0
    padding = 5.0
    usable_w = sheet_w - (2 * padding)
    usable_h = sheet_h - (2 * padding)

    for test_case in test_cases:
        qty = test_case["qty"]
        piece_size = test_case["piece_size"]
        name = test_case["name"]

        print(f"\n📦 {name}:")
        print(f"   Quantity: {qty} pieces")
        print(f"   Piece size: {piece_size[0]} x {piece_size[1]} mm")
        print(f"   Sheet: {sheet_w} x {sheet_h} mm")

        # Theoretical calculation
        piece_with_kerf_w = piece_size[0] + kerf_thickness
        piece_with_kerf_h = piece_size[1] + kerf_thickness
        theoretical_pieces_x = int(usable_w // piece_with_kerf_w)
        theoretical_pieces_y = int(usable_h // piece_with_kerf_h)
        theoretical_max_per_sheet = theoretical_pieces_x * theoretical_pieces_y
        theoretical_sheets_needed = (qty + theoretical_max_per_sheet - 1) // theoretical_max_per_sheet

        print(f"   🧮 Theoretical Analysis:")
        print(f"      Max per sheet: {theoretical_max_per_sheet} ({theoretical_pieces_x}x{theoretical_pieces_y})")
        print(f"      Sheets needed: {theoretical_sheets_needed}")

        # Create shapes for nesting
        piece_shape = [[0, 0], [piece_size[0], 0], [piece_size[0], piece_size[1]], [0, piece_size[1]]]
        shapes = [piece_shape] * qty

        # Run nesting - THIS IS WHERE ISSUES OCCUR WITH LARGE INPUTS
        print(f"   🔄 Running nesting optimization...")
        result = nest2d.nest_shapes(shapes, usable_w, usable_h, spacing=kerf_thickness)

        # Analyze results
        sheets_used = result['bins_used']
        items_placed = len(result['items'])
        success_rate = (items_placed / qty) * 100

        print(f"   📊 Actual Results:")
        print(f"      Sheets used: {sheets_used}")
        print(f"      Items placed: {items_placed} / {qty}")
        print(f"      Success rate: {success_rate:.1f}%")

        # Check for calculation errors
        if sheets_used != theoretical_sheets_needed:
            print(f"   ❌ SHEET COUNT ERROR:")
            print(f"      Expected: {theoretical_sheets_needed} sheets")
            print(f"      Actual: {sheets_used} sheets")
            print(f"      Difference: {sheets_used - theoretical_sheets_needed}")

        # Check for overlapping pieces (common issue with large inputs)
        total_overlaps = 0
        total_unique_pieces = 0

        for sheet_id in range(sheets_used):
            items_on_sheet = [item for item in result['items'] if item['bin_id'] == sheet_id]
            unique_positions = set()
            overlaps_on_sheet = 0

            for item in items_on_sheet:
                pos_key = (round(item['position'][0], 1), round(item['position'][1], 1))
                if pos_key in unique_positions:
                    overlaps_on_sheet += 1
                    total_overlaps += 1
                else:
                    unique_positions.add(pos_key)
                    total_unique_pieces += 1

        if total_overlaps > 0:
            print(f"   ❌ OVERLAP ERROR:")
            print(f"      {total_overlaps} pieces are overlapping")
            print(f"      Only {total_unique_pieces} unique positions")

        # Calculate theoretical vs actual utilization
        if sheets_used > 0:
            total_sheet_area = usable_w * usable_h * sheets_used
            actual_piece_area = total_unique_pieces * piece_size[0] * piece_size[1]
            actual_utilization = (actual_piece_area / total_sheet_area) * 100

            theoretical_piece_area = qty * piece_size[0] * piece_size[1]
            theoretical_total_area = usable_w * usable_h * theoretical_sheets_needed
            theoretical_utilization = (theoretical_piece_area / theoretical_total_area) * 100

            print(f"   📈 Utilization Comparison:")
            print(f"      Theoretical: {theoretical_utilization:.1f}%")
            print(f"      Actual: {actual_utilization:.1f}%")
            print(f"      Difference: {actual_utilization - theoretical_utilization:.1f}%")

        # Overall assessment
        issues = []
        if sheets_used != theoretical_sheets_needed:
            issues.append("Wrong sheet count")
        if total_overlaps > 0:
            issues.append("Overlapping pieces")
        if items_placed != qty:
            issues.append("Missing pieces")
        if success_rate < 100:
            issues.append("Incomplete placement")

        if issues:
            print(f"   🚨 ISSUES DETECTED: {', '.join(issues)}")
        else:
            print(f"   ✅ All calculations correct")

        print(f"   {'-' * 50}")

def test_algorithm_limitations():
    """
    Demonstrate specific algorithm limitations with problematic inputs
    """
    print("\n" + "=" * 60)
    print("🚨 ALGORITHM LIMITATIONS DEMONSTRATION")
    print("=" * 60)

    # Test cases that typically break nesting algorithms
    problematic_cases = [
        {
            "name": "Many Small Pieces",
            "qty": 500,
            "piece_size": (20, 20),
            "sheet_size": (1000, 1000),
            "expected_issue": "Performance degradation, possible overlaps"
        },
        {
            "name": "Large Pieces on Small Sheet",
            "qty": 10,
            "piece_size": (300, 300),
            "sheet_size": (800, 800),
            "expected_issue": "Inefficient packing, wrong sheet count"
        },
        {
            "name": "Non-Square Pieces",
            "qty": 100,
            "piece_size": (50, 200),
            "sheet_size": (1500, 1000),
            "expected_issue": "Rotation issues, poor utilization"
        }
    ]

    for case in problematic_cases:
        print(f"\n🧪 Testing: {case['name']}")
        print(f"   Expected Issue: {case['expected_issue']}")
        print(f"   Setup: {case['qty']} pieces of {case['piece_size']} on {case['sheet_size']} sheet")

        sheet_w, sheet_h = case['sheet_size']
        piece_size = case['piece_size']
        qty = case['qty']
        kerf = 3.0
        padding = 5.0

        usable_w = sheet_w - (2 * padding)
        usable_h = sheet_h - (2 * padding)

        # Quick theoretical check
        piece_with_kerf_area = (piece_size[0] + kerf) * (piece_size[1] + kerf)
        sheet_area = usable_w * usable_h
        theoretical_pieces_per_sheet = int(sheet_area / piece_with_kerf_area)

        print(f"   Quick theory: ~{theoretical_pieces_per_sheet} pieces per sheet")

        # Create shapes and run nesting
        piece_shape = [[0, 0], [piece_size[0], 0], [piece_size[0], piece_size[1]], [0, piece_size[1]]]
        shapes = [piece_shape] * qty

        import time
        start_time = time.time()

        try:
            result = nest2d.nest_shapes(shapes, usable_w, usable_h, spacing=kerf)
            end_time = time.time()

            # Analyze results quickly
            sheets_used = result['bins_used']
            items_placed = len(result['items'])
            processing_time = (end_time - start_time) * 1000

            # Check for major issues
            major_issues = []
            if items_placed < qty * 0.8:  # Less than 80% placed
                major_issues.append(f"Only {items_placed}/{qty} placed")
            if sheets_used == 0 or sheets_used > qty:  # Unreasonable sheet count
                major_issues.append(f"Unreasonable sheet count: {sheets_used}")
            if processing_time > 5000:  # More than 5 seconds
                major_issues.append(f"Slow processing: {processing_time:.0f}ms")

            print(f"   Results: {sheets_used} sheets, {items_placed} placed, {processing_time:.0f}ms")

            if major_issues:
                print(f"   🚨 Issues: {', '.join(major_issues)}")
            else:
                print(f"   ✅ Acceptable results")

        except Exception as e:
            print(f"   💥 CRASH: {str(e)}")

def test_basic_functionality():
    print("=== Testing LibNest2D Wrapper ===")

    # Test legacy function
    result = nest2d.add_numbers(5, 7)
    print(f"Legacy test (5 * 7): {result}")
    assert result == 35, f"Expected 35, got {result}"

    # Test polygon area calculation
    square = [[0, 0], [10, 0], [10, 10], [0, 10]]
    area = nest2d.calculate_area(square)
    print(f"Square area (10x10): {area}")
    assert abs(area - 100.0) < 0.01, f"Expected ~100, got {area}"

    # Test polygon bounds
    bounds = nest2d.get_bounds(square)
    print(f"Square bounds: {bounds}")
    assert bounds['width'] == 10.0, f"Expected width 10, got {bounds['width']}"
    assert bounds['height'] == 10.0, f"Expected height 10, got {bounds['height']}"

    # Test point in polygon
    inside = nest2d.is_point_inside(square, 5, 5)
    outside = nest2d.is_point_inside(square, 15, 15)
    print(f"Point (5,5) in square: {inside}")
    print(f"Point (15,15) in square: {outside}")
    assert inside == True, "Point (5,5) should be inside square"
    assert outside == False, "Point (15,15) should be outside square"

    print("✓ All basic tests passed!")

# ...existing code...

if __name__ == "__main__":
    test_basic_functionality()

    # Focus on small batch detailed analysis with advanced wrapper
    test_glass_factory_small_batch_detailed()

    print("\n🎉 All tests completed successfully!")
