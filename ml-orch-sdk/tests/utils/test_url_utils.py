import pytest

from mlorchsdk import add_params

class TestUrlUtils:
    def test_add_params(self):
        url = "http://example.com/api/123/details"
        query_params = {"key1": "value1", "key2": "value2"}

        expected_url = "http://example.com/api/123/details?key1=value1&key2=value2"
        result_url = add_params(url, query_params)

        assert result_url == expected_url

    def test_add_params_with_special_charaters(self):
        url = "http://example.com/v1/hi"
        query_params = {"key": "value with space & special chars"}

        assert "http://example.com/v1/hi?key=value+with+space+%26+special+chars" == add_params(url, query_params)

    def test_add_params_with_no_query_params(self):
        url = "http://example.com/api/123/details"
        query_params = {}
        expected_url = "http://example.com/api/123/details"
        result_url = add_params(url, query_params)

        assert result_url == expected_url

if __name__ == "__main__":
    pytest.main()