"""
Simple Test Script for LibNest2D Coordinate System Bindings

This is a simple Python script (not unittest) that verifies coordinate system functionality
using static test values. It runs outside Odoo environment for easy testing.
"""

from custom.addons.nesting_optimizer.libs.python_bindings.python.geometry.coordinate import *

def test_coordinate_system():
    """Run all coordinate system tests"""

    print("🚀 LibNest2D Coordinate System Simple Test")
    print("=" * 50)

    try:
        test_count = 0
        passed_tests = 0

        # Test 1: Basic imports and constants
        print("\n🧪 Test 1: Basic Imports and Constants")
        test_count += 1

        try:
            assert MM_IN_COORDS == 1000000, f"Expected MM_IN_COORDS=1000000, got {MM_IN_COORDS}"
            assert callable(mm), "mm should be a function"
            assert callable(coord_to_mm), "coord_to_mm should be a function"
            print("  ✅ Constants and functions imported correctly")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 2: Coord type creation
        print("\n🧪 Test 2: Coord Type Creation")
        test_count += 1

        try:
            coord1 = Coord()
            coord2 = Coord(1000000)

            assert int(coord1) == 0, f"Default Coord should be 0, got {int(coord1)}"
            assert int(coord2) == 1000000, f"Coord(1000000) should be 1000000, got {int(coord2)}"

            # Test string representations
            assert str(coord2) == "1000000", f"str(coord) failed, got {str(coord2)}"
            assert repr(coord2) == "Coord(1000000)", f"repr(coord) failed, got {repr(coord2)}"

            print("  ✅ Coord type creation and conversion works")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 3: Unit conversions
        print("\n🧪 Test 3: Unit Conversions")
        test_count += 1

        try:
            # mile mater to coord
            coord = mm(10.5)
            assert int(coord) == 10500000, f"mm(10.5) should be 10500000, got {int(coord)}"

            # coord to mm
            back_mm = coord_to_mm(coord)
            assert abs(back_mm - 10.5) < 1e-6, f"coord_to_mm round-trip failed: {back_mm}"

            # Test specific conversions
            coord_25_4 = mm(25.4)  # 1 inch
            assert int(coord_25_4) == 25400000, "25.4mm conversion failed"

            print(f"  ✅ Unit conversions work: mm(10.5)={int(coord)}, back={back_mm}")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 4: Arithmetic operations
        print("\n🧪 Test 4: Arithmetic Operations")
        test_count += 1

        try:
            a = Coord(2000000)  # 2mm
            b = Coord(3000000)  # 3mm

            # Test addition
            result_add = a + b
            assert int(result_add) == 5000000, f"2mm + 3mm should be 5mm, got {int(result_add)}"

            # Test subtraction
            result_sub = b - a
            assert int(result_sub) == 1000000, f"3mm - 2mm should be 1mm, got {int(result_sub)}"

            # Test multiplication
            result_mul = a * Coord(2)
            assert int(result_mul) == 4000000, f"2mm * 2 should be 4mm, got {int(result_mul)}"

            print("  ✅ Arithmetic operations work correctly")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 5: Comparison operations
        print("\n🧪 Test 5: Comparison Operations")
        test_count += 1

        try:
            small = Coord(1000000)  # 1mm
            large = Coord(2000000)  # 2mm
            equal = Coord(1000000)  # 1mm

            assert small == equal, "Equal coordinates should be equal"
            assert small != large, "Different coordinates should not be equal"
            assert small < large, "Small should be less than large"
            assert large > small, "Large should be greater than small"
            assert small <= equal, "Small should be <= equal"
            assert small >= equal, "Small should be >= equal"

            print("  ✅ Comparison operations work correctly")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 6: Convenience unit functions
        print("\n🧪 Test 6: Convenience Unit Functions")
        test_count += 1

        try:
            # 1 inch = 25.4mm = 2.54cm
            inch_coord = from_inches(1.0)
            cm_coord = from_cm(2.54)
            mm_coord = from_mm(25.4)

            expected = 25400000  # 25.4 * 1000000

            assert int(inch_coord) == expected, f"1 inch should be {expected}, got {int(inch_coord)}"
            assert int(cm_coord) == expected, f"2.54cm should be {expected}, got {int(cm_coord)}"
            assert int(mm_coord) == expected, f"25.4mm should be {expected}, got {int(mm_coord)}"

            print("  ✅ All convenience unit functions work (1 inch = 2.54cm = 25.4mm)")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 7: High-level Python interface
        print("\n🧪 Test 7: High-Level Python Interface")
        test_count += 1

        try:
            # Test Coordinate class
            coord_mm = Coordinate.create_coord(25.4, 'mm')
            coord_inch = Coordinate.create_coord(1.0, 'inches')

            assert int(coord_mm) == int(coord_inch), "25.4mm should equal 1 inch"

            # Test conversions
            mm_value = Coordinate.to_unit(coord_mm, 'mm')
            inch_value = Coordinate.to_unit(coord_mm, 'inches')

            assert abs(mm_value - 25.4) < 0.01, f"Should convert to 25.4mm, got {mm_value}"
            assert abs(inch_value - 1.0) < 0.01, f"Should convert to 1 inch, got {inch_value}"

            # Test formatting
            formatted = Coordinate.format_coord(coord_mm, 'mm', 1)
            assert "25.4" in formatted and "mm" in formatted, f"Formatting failed: {formatted}"

            print(f"  ✅ High-level interface works: {formatted}")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 8: Point creation and coordinate ranges
        print("\n🧪 Test 8: Point Creation and Ranges")
        test_count += 1

        try:
            # Test create_point
            x, y = create_point(10.5, 20.3, 'mm')
            assert int(x) == 10500000, f"X should be 10500000, got {int(x)}"
            assert int(y) == 20300000, f"Y should be 20300000, got {int(y)}"

            # Test coord_range
            coords = coord_range(0, 5, 1, 'mm')
            assert len(coords) == 5, f"Should generate 5 coordinates, got {len(coords)}"
            assert int(coords[0]) == 0, "First coordinate should be 0"
            assert int(coords[4]) == 4000000, "Last coordinate should be 4mm"

            print(f"  ✅ Point creation and ranges work: point=({int(x)}, {int(y)}), range len={len(coords)}")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 9: Validation functions
        print("\n🧪 Test 9: Validation Functions")
        test_count += 1

        try:
            # Test coordinate validation
            small_coord = mm(100)       # 100mm - reasonable
            large_coord = mm(10000000)  # 10km - too large

            assert validate_coord(small_coord) == True, "100mm should be valid"
            assert validate_coord(large_coord) == False, "10km should be invalid"

            # Test dimension validation
            width = mm(100)
            height = mm(200)
            zero_dim = Coord(0)
            negative_dim = Coord(-1000000)

            assert validate_dimensions(width, height) == True, "Positive dimensions should be valid"
            assert validate_dimensions(zero_dim, height) == False, "Zero width should be invalid"
            assert validate_dimensions(width, negative_dim) == False, "Negative height should be invalid"

            print("  ✅ Validation functions work correctly")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Test 10: Real-world scenario
        print("\n🧪 Test 10: Real-World Scenario (US Letter Paper)")
        test_count += 1

        try:
            # US Letter: 8.5" x 11"
            width_inches = 8.5
            height_inches = 11.0

            width_coord = Coordinate.create_coord(width_inches, 'inches')
            height_coord = Coordinate.create_coord(height_inches, 'inches')

            # Convert to mm for verification
            width_mm = Coordinate.to_unit(width_coord, 'mm')
            height_mm = Coordinate.to_unit(height_coord, 'mm')

            expected_width_mm = 8.5 * 25.4  # 215.9mm
            expected_height_mm = 11.0 * 25.4  # 279.4mm

            assert abs(width_mm - expected_width_mm) < 0.1, f"Width: expected {expected_width_mm}mm, got {width_mm}mm"
            assert abs(height_mm - expected_height_mm) < 0.1, f"Height: expected {expected_height_mm}mm, got {height_mm}mm"

            area_mm2 = width_mm * height_mm
            print(f"  ✅ US Letter ({width_inches}\" × {height_inches}\") = {width_mm:.1f}mm × {height_mm:.1f}mm = {area_mm2:.0f} mm²")
            passed_tests += 1
        except Exception as exception:
            print(f"  ❌ Failed: {exception}")

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {test_count}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {test_count - passed_tests}")

        if passed_tests == test_count:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Your LibNest2D coordinate bindings are working perfectly!")
            print("\n💡 Next steps:")
            print("   • Your coordinate system is fully functional")
            print("   • You can proceed to implement Point bindings (Phase 1.2)")
            print("   • All unit conversions and operations work correctly")
            return True
        else:
            print(f"\n⚠️  {test_count - passed_tests} test(s) failed!")
            print("❌ Fix the issues before proceeding to next phase")
            return False

    except ImportError as exception:
        print(f"\n❌ Import Error: {exception}")
        print("\n🔧 Possible fixes:")
        print("1. Make sure you've built the C++ module:")
        print("   cd build && cmake .. && make")
        print("2. Check that the nest2d module exists in build/")
        print("3. Verify the Python interface is properly set up")
        return False

    except Exception as exception:
        print(f"\n💥 Unexpected Error: {exception}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_coordinate_system()
    print(f"\n{'🎊 SUCCESS' if success else '🛠️  NEEDS WORK'}")
    sys.exit(0 if success else 1)
