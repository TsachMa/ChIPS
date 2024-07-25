import unittest
import os
import decoration_and_initialization as di

class TestAdjustKpointSpacing(unittest.TestCase):

    def test_adjust_kpoint_spacing(self):
        # Prepare a test file
        
        source_file_name = "/home/riesel/CASTEP/Hisono_calcs/ambient_pressure/LaRu4Bi12/ternaries/La3RuBi5.cell"
        test_file_name = "/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts/TestFolder/La3RuBi5_test.cell"
        test_kpoint_spacing = 0.1
        check_file_name = "/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts/TestFolder/La3RuBi5_check.cell"

        with open(source_file_name, "r") as file:
            content_before = file.read()

        with open(test_file_name, "w") as file:
            file.write(content_before)

        # Run the function to adjust the kpoint spacing
        di.adjust_kpoint_spacing(test_file_name, test_kpoint_spacing)

        # Check the content of the file after running the function
        with open(test_file_name, "r") as file:
            content_after = file.read()

        # Check the content of the check file
        with open(check_file_name, "r") as file:
            expected_content = file.read()

        # Assert that the content matches the expected content
        self.assertEqual(content_after, expected_content)

    def test_adjust_pressure(self):
        # Prepare a test file
        source_file_name = "/home/riesel/CASTEP/Hisono_calcs/ambient_pressure/LaRu4Bi12/ternaries/La3RuBi5.cell"
        test_file_name = "/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts/TestFolder/La3RuBi5_test_pressure.cell"
        test_pressure = 0
        check_file_name = "/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts/TestFolder/La3RuBi5_check_pressure.cell"

        with open(source_file_name, "r") as file:
            content_before = file.read()

        with open(test_file_name, "w") as file:
            file.write(content_before)

        # Run the function to adjust the pressure
        di.adjust_pressure(test_file_name, test_pressure)

        # Check the content of the file after running the function
        with open(test_file_name, "r") as file:
            content_after = file.read()

        # Check the content of the check file
        with open(check_file_name, "r") as file:
            expected_content = file.read()

        # Assert that the content matches the expected content
        self.assertEqual(content_after, expected_content)

if __name__ == "__main__":
    unittest.main()
