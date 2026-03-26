"""Smoke tests to verify basic functionality"""
import unittest


class TestSmoke(unittest.TestCase):
    """Basic smoke tests"""
    
    def test_imports(self):
        """Test that main modules can be imported"""
        try:
            import app.app
            import src.data.preprocess
            import src.model.train
            import src.utils.s3_utils
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")
    
    def test_python_version(self):
        """Test Python version compatibility"""
        import sys
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 7)


if __name__ == '__main__':
    unittest.main()
