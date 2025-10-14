"""
End-to-End Conversion Tests

Tests the complete conversion pipeline from JMeter JMX to LoadRunner C scripts.
These tests use real sample files and validate the entire conversion process.
"""

import pytest
import os
import glob
from converters.jmeter_to_lr import JMeterToLRConverter
from utils.validators import validate_file_extension, validate_file_size


# Test configuration
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'samples')
MIN_CONVERSION_ACCURACY = 0.80  # 80% minimum accuracy target


class TestEndToEndConversion:
    """End-to-End conversion test suite"""

    @pytest.fixture
    def converter(self):
        """Create a converter instance for each test"""
        return JMeterToLRConverter()

    @pytest.fixture
    def sample_files(self):
        """Get all sample JMX files"""
        pattern = os.path.join(SAMPLES_DIR, '*.jmx')
        files = glob.glob(pattern)
        if not files:
            pytest.skip(f"No sample JMX files found in {SAMPLES_DIR}")
        return files

    def test_samples_directory_exists(self):
        """Verify samples directory exists"""
        assert os.path.exists(SAMPLES_DIR), f"Samples directory not found: {SAMPLES_DIR}"

    def test_sample_files_available(self, sample_files):
        """Verify sample files are available"""
        assert len(sample_files) >= 10, f"Expected at least 10 sample files, found {len(sample_files)}"

    def test_01_simple_get_conversion(self, converter):
        """Test conversion of simple GET request"""
        jmx_file = os.path.join(SAMPLES_DIR, '01_simple_get.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        # Validate input
        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid, f"Input validation failed: {error}"

        # Convert
        result = converter.convert(jmx_content)
        assert result['success'], f"Conversion failed: {result.get('errors', [])}"

        # Generate output
        lr_script = converter.generate_output(result['data'])
        assert lr_script, "Generated script is empty"

        # Verify basic structure
        assert '#include "web_api.h"' in lr_script
        assert 'vuser_init()' in lr_script
        assert 'Action()' in lr_script
        assert 'vuser_end()' in lr_script
        assert 'web_url(' in lr_script
        assert 'LAST' in lr_script

        print(f"\n[OK] 01_simple_get conversion successful")
        print(f"  Generated script length: {len(lr_script)} chars")

    def test_02_post_with_params_conversion(self, converter):
        """Test conversion of POST request with parameters"""
        jmx_file = os.path.join(SAMPLES_DIR, '02_post_with_params.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify POST conversion
        assert 'web_submit_data(' in lr_script or 'web_custom_request(' in lr_script
        assert 'username' in lr_script
        assert 'password' in lr_script

        print(f"\n[OK] 02_post_with_params conversion successful")

    def test_03_with_headers_conversion(self, converter):
        """Test conversion of request with headers"""
        jmx_file = os.path.join(SAMPLES_DIR, '03_with_headers.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify headers
        assert 'web_add_header(' in lr_script
        assert 'Content-Type' in lr_script or 'application/json' in lr_script

        print(f"\n[OK] 03_with_headers conversion successful")

    def test_04_with_regex_extractor_conversion(self, converter):
        """Test conversion of regex extractor (correlation)"""
        jmx_file = os.path.join(SAMPLES_DIR, '04_with_regex_extractor.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify correlation
        assert 'web_reg_save_param(' in lr_script or 'web_reg_save_param_regexp(' in lr_script
        assert 'token' in lr_script

        print(f"\n[OK] 04_with_regex_extractor conversion successful")

    def test_05_with_json_extractor_conversion(self, converter):
        """Test conversion of JSON extractor"""
        jmx_file = os.path.join(SAMPLES_DIR, '05_with_json_extractor.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify JSON extraction
        assert 'web_reg_save_param_json(' in lr_script or 'userId' in lr_script

        print(f"\n[OK] 05_with_json_extractor conversion successful")

    def test_06_with_timer_conversion(self, converter):
        """Test conversion of timer (think time)"""
        jmx_file = os.path.join(SAMPLES_DIR, '06_with_timer.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify think time
        assert 'lr_think_time(' in lr_script

        print(f"\n[OK] 06_with_timer conversion successful")

    def test_07_with_transaction_conversion(self, converter):
        """Test conversion of transaction controller"""
        jmx_file = os.path.join(SAMPLES_DIR, '07_with_transaction.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify transactions
        assert 'lr_start_transaction(' in lr_script
        assert 'lr_end_transaction(' in lr_script

        print(f"\n[OK] 07_with_transaction conversion successful")

    def test_08_with_loop_controller_conversion(self, converter):
        """Test conversion of loop controller"""
        jmx_file = os.path.join(SAMPLES_DIR, '08_with_loop_controller.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify loop
        assert 'for' in lr_script or 'while' in lr_script or '/* Loop' in lr_script

        print(f"\n[OK] 08_with_loop_controller conversion successful")

    def test_09_with_if_controller_conversion(self, converter):
        """Test conversion of if controller"""
        jmx_file = os.path.join(SAMPLES_DIR, '09_with_if_controller.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify conditional
        assert 'if' in lr_script or '/* If' in lr_script

        print(f"\n[OK] 09_with_if_controller conversion successful")

    def test_10_complex_scenario_conversion(self, converter):
        """Test conversion of complex e-commerce scenario"""
        jmx_file = os.path.join(SAMPLES_DIR, '10_complex_scenario.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        is_valid, error = converter.validate_input(jmx_content)
        assert is_valid

        result = converter.convert(jmx_content)
        assert result['success']

        lr_script = converter.generate_output(result['data'])
        assert lr_script

        # Verify complex elements
        assert 'web_url(' in lr_script or 'web_custom_request(' in lr_script
        assert 'web_add_header(' in lr_script
        assert 'lr_start_transaction(' in lr_script
        assert 'lr_end_transaction(' in lr_script
        assert 'web_reg_save_param' in lr_script

        # Verify variables
        assert 'BASE_URL' in lr_script or 'sessionId' in lr_script or 'productId' in lr_script

        print(f"\n[OK] 10_complex_scenario conversion successful")

    def test_all_samples_batch_conversion(self, converter, sample_files):
        """Batch test all sample files"""
        results = []

        for jmx_file in sample_files:
            filename = os.path.basename(jmx_file)

            try:
                with open(jmx_file, 'r', encoding='utf-8') as f:
                    jmx_content = f.read()

                # Validate
                is_valid, error = converter.validate_input(jmx_content)
                if not is_valid:
                    results.append({
                        'file': filename,
                        'success': False,
                        'error': f"Validation failed: {error}"
                    })
                    continue

                # Convert
                result = converter.convert(jmx_content)
                if not result['success']:
                    results.append({
                        'file': filename,
                        'success': False,
                        'error': f"Conversion failed: {result.get('errors', [])}"
                    })
                    continue

                # Generate
                lr_script = converter.generate_output(result['data'])
                if not lr_script or len(lr_script) < 100:
                    results.append({
                        'file': filename,
                        'success': False,
                        'error': "Generated script too short or empty"
                    })
                    continue

                results.append({
                    'file': filename,
                    'success': True,
                    'script_length': len(lr_script),
                    'warnings': len(result.get('warnings', [])),
                    'errors': len(result.get('errors', []))
                })

            except Exception as e:
                results.append({
                    'file': filename,
                    'success': False,
                    'error': str(e)
                })

        # Print summary
        print("\n" + "=" * 70)
        print("BATCH CONVERSION SUMMARY")
        print("=" * 70)

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"Total Files: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Success Rate: {len(successful) / len(results) * 100:.1f}%")
        print()

        if successful:
            print("Successful Conversions:")
            for result in successful:
                print(f"  [OK] {result['file']}")
                print(f"    - Script length: {result['script_length']} chars")
                print(f"    - Warnings: {result['warnings']}, Errors: {result['errors']}")

        if failed:
            print("\nFailed Conversions:")
            for result in failed:
                print(f"  [FAIL] {result['file']}")
                print(f"    - Error: {result['error']}")

        print("=" * 70)

        # Assert minimum success rate
        success_rate = len(successful) / len(results)
        assert success_rate >= MIN_CONVERSION_ACCURACY, \
            f"Success rate {success_rate:.1%} below minimum {MIN_CONVERSION_ACCURACY:.1%}"

    def test_conversion_statistics(self, converter):
        """Test conversion statistics tracking"""
        jmx_file = os.path.join(SAMPLES_DIR, '10_complex_scenario.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        converter.validate_input(jmx_content)
        result = converter.convert(jmx_content)
        lr_script = converter.generate_output(result['data'])

        # Get statistics
        stats = converter.conversion_stats

        assert 'items_total' in stats
        assert 'items_converted' in stats
        assert 'items_skipped' in stats

        print(f"\n[OK] Conversion statistics:")
        print(f"  Total items: {stats['items_total']}")
        print(f"  Converted: {stats['items_converted']}")
        print(f"  Skipped: {stats['items_skipped']}")

    def test_conversion_warnings_and_errors(self, converter):
        """Test that warnings and errors are properly captured"""
        jmx_file = os.path.join(SAMPLES_DIR, '10_complex_scenario.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        result = converter.convert(jmx_content)

        # Check that warnings list exists (may be empty)
        assert 'warnings' in result
        assert isinstance(result['warnings'], list)

        # Check errors list exists
        assert 'errors' in result
        assert isinstance(result['errors'], list)

        # For complex scenario, we expect some warnings
        if result['warnings']:
            print(f"\n[OK] Warnings captured: {len(result['warnings'])}")
            for warning in result['warnings'][:3]:  # Show first 3
                print(f"  [WARN] {warning}")

    def test_generated_script_syntax(self, converter):
        """Test that generated script has valid C syntax basics"""
        jmx_file = os.path.join(SAMPLES_DIR, '01_simple_get.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        result = converter.convert(jmx_content)
        lr_script = converter.generate_output(result['data'])

        # Check for balanced braces
        open_braces = lr_script.count('{')
        close_braces = lr_script.count('}')
        assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

        # Check for balanced parentheses in function definitions
        assert lr_script.count('vuser_init(') == 1
        assert lr_script.count('Action(') == 1
        assert lr_script.count('vuser_end(') == 1

        # Check for required return statements
        assert 'return 0;' in lr_script

        print(f"\n[OK] Generated script syntax checks passed")
        print(f"  Open/Close braces: {open_braces}/{close_braces}")

    def test_empty_input_handling(self, converter):
        """Test handling of empty input"""
        is_valid, error = converter.validate_input("")
        assert not is_valid
        assert error is not None

    def test_invalid_xml_handling(self, converter):
        """Test handling of invalid XML"""
        invalid_xml = "<invalid>Not a JMX file</invalid>"
        is_valid, error = converter.validate_input(invalid_xml)
        assert not is_valid

    def test_missing_testplan_handling(self, converter):
        """Test handling of XML without TestPlan"""
        invalid_jmx = """<?xml version="1.0" encoding="UTF-8"?>
        <jmeterTestPlan>
            <hashTree>
                <SomeOtherElement/>
            </hashTree>
        </jmeterTestPlan>"""

        is_valid, error = converter.validate_input(invalid_jmx)
        assert not is_valid


class TestConversionOutput:
    """Test the quality of conversion output"""

    @pytest.fixture
    def converter(self):
        return JMeterToLRConverter()

    def test_output_has_proper_structure(self, converter):
        """Test that output follows LoadRunner C script structure"""
        jmx_file = os.path.join(SAMPLES_DIR, '01_simple_get.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        result = converter.convert(jmx_content)
        lr_script = converter.generate_output(result['data'])

        # Check structure order
        init_pos = lr_script.find('vuser_init()')
        action_pos = lr_script.find('Action()')
        end_pos = lr_script.find('vuser_end()')

        assert init_pos < action_pos < end_pos, \
            "Functions not in correct order: vuser_init -> Action -> vuser_end"

    def test_output_has_comments(self, converter):
        """Test that output includes helpful comments"""
        jmx_file = os.path.join(SAMPLES_DIR, '01_simple_get.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        result = converter.convert(jmx_content)
        lr_script = converter.generate_output(result['data'])

        # Check for comments
        assert '/*' in lr_script or '//' in lr_script, "No comments found in generated script"

    def test_output_formatting(self, converter):
        """Test that output is properly formatted"""
        jmx_file = os.path.join(SAMPLES_DIR, '01_simple_get.jmx')
        if not os.path.exists(jmx_file):
            pytest.skip(f"Sample file not found: {jmx_file}")

        with open(jmx_file, 'r', encoding='utf-8') as f:
            jmx_content = f.read()

        result = converter.convert(jmx_content)
        lr_script = converter.generate_output(result['data'])

        # Check for proper indentation (at least some tabs or spaces)
        lines = lr_script.split('\n')
        indented_lines = [l for l in lines if l.startswith('    ') or l.startswith('\t')]

        assert len(indented_lines) > 0, "No indented lines found - script may not be properly formatted"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
