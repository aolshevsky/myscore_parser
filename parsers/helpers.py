from myscore_parser import templates
import re


def change_js_suffix_in_url(url: str, new_suffix: str) -> str:
    return url[: url.find('#')] + new_suffix


def get_id_of_clickable_element(soup):
    id_regex = re.compile('/[\S]*/')
    return id_regex.findall(soup.find('a')['onclick'])


def convert_ids_to_urls(ids: list) -> list:
    result_list = []

    for i in ids:
        url = '{}{}'.format(templates.BASE_URL, i)
        result_list.append(url)

    return result_list


def start_parse_page(bot):
    bot.add_window_handle(bot.driver.window_handles[-1])
    bot.driver.switch_to.window(bot.get_current_window_handel())


def end_parse_page(bot):
    bot.driver.close()
    bot.pop_window_handle()
    bot.driver.switch_to.window(bot.get_current_window_handel())


def go_to_a_new_page(f):
    def wrapper(*args, **kwargs):
        start_parse_page(args[0])
        res = f(*args, **kwargs)
        end_parse_page(args[0])
        return res
    return wrapper



