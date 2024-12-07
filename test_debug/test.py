import ctypes
import requests


def output_debug_string(message):
    ctypes.windll.kernel32.OutputDebugStringW(message)


def crawl_url(url):
    try:
        response = requests.get(url)
        output_debug_string(f"成功请求URL: {url}，状态码: {response.status_code}")
    except requests.RequestException as e:
        output_debug_string(f"请求URL: {url}出错，错误信息: {str(e)}")


crawl_url("abc")
