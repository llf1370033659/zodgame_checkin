import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch


spec = importlib.util.spec_from_file_location(
    "zodgame_script", Path(__file__).parents[1] / "zodgame" / "zodgame.py"
)
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class CookieTests(unittest.TestCase):
    def test_preserves_encoded_auth_and_slashes(self):
        cookies = script.parse_cookies(
            "Cookie: qhMq_2132_saltkey=salt; qhMq_2132_auth=a/b+c==; other=x=y; "
        )
        values = {cookie["name"]: cookie["value"] for cookie in cookies}
        self.assertEqual(values["qhMq_2132_auth"], "a/b+c==")
        self.assertEqual(values["other"], "x=y")

    def test_rejects_missing_authentication_before_browser_start(self):
        with patch.object(script.uc, "Chrome") as chrome:
            with self.assertRaisesRegex(ValueError, "qhMq_2132_auth"):
                script.zodgame("qhMq_2132_saltkey=salt")
            chrome.assert_not_called()

    def test_rejects_malformed_cookie_without_logging_value(self):
        with self.assertRaises(ValueError) as error:
            script.parse_cookies("secret-malformed-value")
        self.assertNotIn("secret-malformed-value", str(error.exception))


class BrowserStartupTests(unittest.TestCase):
    def test_uses_configured_browser_and_closes_on_login_failure(self):
        driver = Mock()
        driver.title = "ZodGame"
        driver.find_elements.return_value = [Mock()]
        configuration = {
            "CHROME_BINARY": "/example/chrome",
            "CHROMEDRIVER_BINARY": "/example/chromedriver",
            "CHROME_VERSION": "151.0.7922.173",
            "ZODGAME_HEADLESS": "1",
        }
        with patch.dict(os.environ, configuration, clear=True):
            with patch.object(script.uc, "Chrome", return_value=driver) as chrome:
                with self.assertRaisesRegex(AssertionError, "Login fails"):
                    script.zodgame("qhMq_2132_saltkey=salt; qhMq_2132_auth=a/b==")
        kwargs = chrome.call_args.kwargs
        self.assertEqual(kwargs["browser_executable_path"], "/example/chrome")
        self.assertEqual(kwargs["driver_executable_path"], "/example/chromedriver")
        self.assertEqual(kwargs["version_main"], 151)
        self.assertTrue(kwargs["headless"])
        self.assertEqual(driver.add_cookie.call_args_list[1].args[0]["value"], "a/b==")
        driver.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
