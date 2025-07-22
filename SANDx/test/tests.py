#!/usr/bin/env python3
"""
Comprehensive test suite for CLI parser
"""

import unittest
import argparse
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open
from io import StringIO
import process_options
try:
    from process_options import (
        parse_machine_list,
        validate_existing_path, 
        validate_output_path,
        create_parser,
        main
    )
except ImportError:

    print("Warning: Could not import process_options module. Ensure it's in the same directory.")
    sys.exit(1)


class TestParseMachineList(unittest.TestCase):
    """Test cases for parse_machine_list function"""
    
    def test_single_machine(self):
        """Test parsing single machine"""
        result = parse_machine_list("machine1")
        self.assertEqual(result, ["machine1"])
    
    def test_multiple_machines(self):
        """Test parsing multiple machines"""
        result = parse_machine_list("machine1,machine2,machine3")
        self.assertEqual(result, ["machine1", "machine2", "machine3"])
    
    def test_machines_with_spaces(self):
        """Test parsing machines with spaces"""
        result = parse_machine_list("machine1, machine2 , machine3")
        self.assertEqual(result, ["machine1", "machine2", "machine3"])
    
    def test_empty_string(self):
        """Test parsing empty string should raise error"""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_machine_list("")
    
    def test_only_commas(self):
        """Test parsing only commas should raise error"""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_machine_list(",,,")
    
    def test_empty_entries_filtered(self):
        """Test that empty entries are filtered out"""
        result = parse_machine_list("machine1,,machine2,")
        self.assertEqual(result, ["machine1", "machine2"])
    
    def test_whitespace_only_entries(self):
        """Test entries with only whitespace"""
        result = parse_machine_list("machine1,   ,machine2")
        self.assertEqual(result, ["machine1", "machine2"])


class TestValidateExistingPath(unittest.TestCase):
    """Test cases for validate_existing_path function"""
    
    def setUp(self):
        """Set up temporary directories for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "testfile.txt")
        with open(self.test_file, 'w') as f:
            f.write("test")
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_valid_directory(self):
        """Test with valid existing directory"""
        result = validate_existing_path(self.test_dir)
        self.assertTrue(result.is_dir())
        self.assertEqual(str(result), str(Path(self.test_dir).resolve()))
    
    def test_nonexistent_path(self):
        """Test with non-existent path"""
        fake_path = os.path.join(self.test_dir, "nonexistent")
        with self.assertRaises(argparse.ArgumentTypeError) as cm:
            validate_existing_path(fake_path)
        self.assertIn("Path does not exist", str(cm.exception))
    
    def test_file_instead_of_directory(self):
        """Test with file instead of directory"""
        with self.assertRaises(argparse.ArgumentTypeError) as cm:
            validate_existing_path(self.test_file)
        self.assertIn("Path is not a directory", str(cm.exception))


class TestValidateOutputPath(unittest.TestCase):
    """Test cases for validate_output_path function"""
    
    def setUp(self):
        """Set up temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_existing_directory(self):
        """Test with existing directory"""
        result = validate_output_path(self.test_dir)
        self.assertTrue(result.is_dir())
        self.assertEqual(str(result), str(Path(self.test_dir).resolve()))
    
    def test_create_new_directory(self):
        """Test creating new directory"""
        new_dir = os.path.join(self.test_dir, "new_output")
        result = validate_output_path(new_dir)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(result.is_dir())
    
    def test_create_nested_directory(self):
        """Test creating nested directory structure"""
        nested_dir = os.path.join(self.test_dir, "level1", "level2", "output")
        result = validate_output_path(nested_dir)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(result.is_dir())
    
    def test_permission_error(self):
        """Test permission error when creating directory"""
        # This test might not work on all systems, so we'll mock it
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")
            with self.assertRaises(argparse.ArgumentTypeError) as cm:
                validate_output_path("/root/forbidden")
            self.assertIn("Cannot create output directory", str(cm.exception))


class TestCLIParser(unittest.TestCase):
    """Test cases for the main CLI parser"""
    
    def setUp(self):
        """Set up temporary directories and parser for testing"""
        self.test_input_dir = tempfile.mkdtemp()
        self.test_output_dir = tempfile.mkdtemp()
        self.parser = create_parser()
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_input_dir, ignore_errors=True)
        shutil.rmtree(self.test_output_dir, ignore_errors=True)
    
    def test_minimal_valid_args(self):
        """Test minimal valid argument set"""
        args = self.parser.parse_args([
            '-i', self.test_input_dir,
            '-m', 'machine1',
            '-c', 'x86',
            '-e', 'dynamic_opcodes',
            '-o', self.test_output_dir
        ])
        
        self.assertEqual(args.num_folders, 1)  # default value
        self.assertEqual(str(args.input_folder), str(Path(self.test_input_dir).resolve()))
        self.assertEqual(args.machines, ['machine1'])
        self.assertEqual(args.cpu, 'x86')
        self.assertEqual(args.experiments, ['dynamic_opcodes'])
        self.assertEqual(str(args.output_folder), str(Path(self.test_output_dir).resolve()))
    
    def test_all_args_long_format(self):
        """Test all arguments using long format"""
        args = self.parser.parse_args([
            '--num-folders', '5',
            '--input-folder', self.test_input_dir,
            '--machines', 'vm1,vm2,vm3',
            '--cpu', 'arm',
            '--experiments', 'dynamic_opcodes', 'syscalls',
            '--output-folder', self.test_output_dir
        ])
        
        self.assertEqual(args.num_folders, 5)
        self.assertEqual(args.machines, ['vm1', 'vm2', 'vm3'])
        self.assertEqual(args.cpu, 'arm')
        self.assertEqual(set(args.experiments), {'dynamic_opcodes', 'syscalls'})
    
    def test_all_cpu_choices(self):
        """Test all valid CPU choices"""
        cpu_choices = ['arm', 'sparc', 'x86', 'm68k', 'mips', 'mipsel', 'powerpc']
        
        for cpu in cpu_choices:
            args = self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', cpu,
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])
            self.assertEqual(args.cpu, cpu)
    
    def test_all_experiment_choices(self):
        """Test all valid experiment choices"""
        experiments = ['dynamic_opcodes', 'static_opcodes', 'syscalls']
        
        # Test single experiments
        for exp in experiments:
            args = self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', 'x86',
                '-e', exp,
                '-o', self.test_output_dir
            ])
            self.assertEqual(args.experiments, [exp])
        
        # Test all experiments together
        args = self.parser.parse_args([
            '-i', self.test_input_dir,
            '-m', 'machine1',
            '-c', 'x86',
            '-e'] + experiments + [
            '-o', self.test_output_dir
        ])
        self.assertEqual(set(args.experiments), set(experiments))
    
    def test_missing_required_input_folder(self):
        """Test missing required input folder"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-m', 'machine1',
                '-c', 'x86',
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])
    
    def test_missing_required_machines(self):
        """Test missing required machines"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', self.test_input_dir,
                '-c', 'x86',
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])
    
    def test_missing_required_cpu(self):
        """Test missing required CPU"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])
    
    def test_missing_required_experiments(self):
        """Test missing required experiments"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', 'x86',
                '-o', self.test_output_dir
            ])
    
    def test_missing_required_output_folder(self):
        """Test missing required output folder"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', 'x86',
                '-e', 'dynamic_opcodes'
            ])
    
    def test_invalid_cpu_choice(self):
        """Test invalid CPU choice"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', 'invalid_cpu',
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])
    
    def test_invalid_experiment_choice(self):
        """Test invalid experiment choice"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', 'x86',
                '-e', 'invalid_experiment',
                '-o', self.test_output_dir
            ])
    
    def test_invalid_num_folders_type(self):
        """Test invalid num_folders type"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-n', 'not_a_number',
                '-i', self.test_input_dir,
                '-m', 'machine1',
                '-c', 'x86',
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])
    
    def test_negative_num_folders(self):
        """Test negative num_folders (should be allowed by parser but might be invalid for application)"""
        args = self.parser.parse_args([
            '-n', '-5',
            '-i', self.test_input_dir,
            '-m', 'machine1',
            '-c', 'x86',
            '-e', 'dynamic_opcodes',
            '-o', self.test_output_dir
        ])
        self.assertEqual(args.num_folders, -5)
    
    def test_zero_num_folders(self):
        """Test zero num_folders"""
        args = self.parser.parse_args([
            '-n', '0',
            '-i', self.test_input_dir,
            '-m', 'machine1',
            '-c', 'x86',
            '-e', 'dynamic_opcodes',
            '-o', self.test_output_dir
        ])
        self.assertEqual(args.num_folders, 0)
    
    def test_nonexistent_input_directory(self):
        """Test non-existent input directory"""
        fake_dir = "/path/that/does/not/exist"
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                '-i', fake_dir,
                '-m', 'machine1',
                '-c', 'x86',
                '-e', 'dynamic_opcodes',
                '-o', self.test_output_dir
            ])


class TestMainFunction(unittest.TestCase):
    """Test cases for the main function"""
    
    def setUp(self):
        """Set up temporary directories for testing"""
        self.test_input_dir = tempfile.mkdtemp()
        self.test_output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_input_dir, ignore_errors=True)
        shutil.rmtree(self.test_output_dir, ignore_errors=True)
    
    @patch('sys.argv')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_with_valid_args(self, mock_stdout, mock_argv):
        """Test main function with valid arguments"""
        mock_argv.return_value = [
            'test_script',
            '-i', self.test_input_dir,
            '-m', 'machine1,machine2',
            '-c', 'x86',
            '-e', 'dynamic_opcodes', 'syscalls',
            '-o', self.test_output_dir,
            '-n', '3'
        ]
        
        args = main()
        
        # Check that configuration was printed
        output = mock_stdout.getvalue()
        self.assertIn("Configuration:", output)
        self.assertIn("Number of folders: 3", output)
        self.assertIn("machine1, machine2", output)
        self.assertIn("CPU target: x86", output)
        self.assertIn("dynamic_opcodes, syscalls", output)
        
        # Check returned args
        self.assertEqual(args.num_folders, 3)
        self.assertEqual(args.machines, ['machine1', 'machine2'])
        self.assertEqual(args.cpu, 'x86')
        self.assertEqual(set(args.experiments), {'dynamic_opcodes', 'syscalls'})
    
    @patch('sys.argv')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_with_invalid_args(self, mock_stderr, mock_argv):
        """Test main function with invalid arguments"""
        mock_argv.return_value = [
            'test_script',
            '-i', '/nonexistent/path',
            '-m', 'machine1',
            '-c', 'x86',
            '-e', 'dynamic_opcodes',
            '-o', self.test_output_dir
        ]
        
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 1)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for common usage scenarios"""
    
    def setUp(self):
        """Set up temporary directories for testing"""
        self.test_input_dir = tempfile.mkdtemp()
        self.parser = create_parser()
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_input_dir, ignore_errors=True)
    
    def test_research_scenario(self):
        """Test typical research scenario"""
        new_output = os.path.join(tempfile.gettempdir(), "research_output")
        args = self.parser.parse_args([
            '--num-folders', '10',
            '--input-folder', self.test_input_dir,
            '--machines', 'cluster1,cluster2,cluster3,cluster4',
            '--cpu', 'arm',
            '--experiments', 'dynamic_opcodes', 'static_opcodes', 'syscalls',
            '--output-folder', new_output
        ])
        
        self.assertEqual(args.num_folders, 10)
        self.assertEqual(len(args.machines), 4)
        self.assertEqual(len(args.experiments), 3)
        self.assertTrue(os.path.exists(new_output))
        
        # Clean up
        shutil.rmtree(new_output, ignore_errors=True)
    
    def test_single_machine_quick_test(self):
        """Test single machine, single experiment scenario"""
        output_dir = tempfile.mkdtemp()
        args = self.parser.parse_args([
            '-i', self.test_input_dir,
            '-m', 'localhost',
            '-c', 'x86',
            '-e', 'syscalls',
            '-o', output_dir
        ])
        
        self.assertEqual(args.num_folders, 1)  # default
        self.assertEqual(args.machines, ['localhost'])
        self.assertEqual(args.experiments, ['syscalls'])
        
        # Clean up
        shutil.rmtree(output_dir, ignore_errors=True)
    
    def test_mixed_architectures_comprehensive(self):
        """Test scenario with different architectures"""
        architectures = ['arm', 'x86', 'mips', 'powerpc']
        
        for arch in architectures:
            output_dir = tempfile.mkdtemp()
            args = self.parser.parse_args([
                '-n', '2',
                '-i', self.test_input_dir,
                '-m', f'{arch}_machine1,{arch}_machine2',
                '-c', arch,
                '-e', 'dynamic_opcodes', 'static_opcodes',
                '-o', output_dir
            ])
            
            self.assertEqual(args.cpu, arch)
            self.assertEqual(len(args.machines), 2)
            self.assertTrue(all(arch in machine for machine in args.machines))
            
            # Clean up
            shutil.rmtree(output_dir, ignore_errors=True)


if __name__ == '__main__':
    # Create a test suite that includes all test cases
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestParseMachineList,
        TestValidateExistingPath,
        TestValidateOutputPath,
        TestCLIParser,
        TestMainFunction,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)