import re


def change_js_postfix_in_url(url: str, new_postfix):
    return url[: url.find('#')] + new_postfix
