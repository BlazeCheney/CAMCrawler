import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import db.pg_db
from common.link_check import ensure_https_link


def fetch_page(url):
    """
    获取指定新闻栏目所有分页链接。
    :param url: 新闻栏目首页URL
    :return: 分页链接列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(ensure_https_link(url), headers=headers)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        lastpage_div = soup.find('div', id='channelPage')
        lastpage_links = lastpage_div.find_all('a') if lastpage_div else []

        lastpage = lastpage_links[-2].text if lastpage_links else "0"

        if int(lastpage) <= 0:
            return []

        page_links = [f"{url}{i}/#liststart" for i in range(1, int(lastpage) + 1)]
        return page_links
    except Exception as e:
        print(f"发生错误：{e}")
        return []


def fetch_category_links(url):
    """从主页获取所有类别链接"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.3029.110 Safari/537.3'}
    print(ensure_https_link(url))
    try:
        response = requests.get(ensure_https_link(url), headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 假设子类别链接包含在特定的标签和类中，这里需要根据实际页面结构调整
            category_links = soup.select('#ulNav ul li.nav-item a')  # 请根据实际页面结构调整选择器

            return [link['href'] for link in category_links if link.has_attr('href')]
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return []
    except Exception as e:
        print(f"发生错误：{e}")
        return []


def fetch_news_links(url):
    """获取新闻页面中的所有新闻链接"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.3029.110 Safari/537.3'}
    print(ensure_https_link(url))
    try:
        response = requests.get(ensure_https_link(url), headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 假设新闻链接包含在特定的标签和类中，这里需要根据实际页面结构调整
            news_links = soup.select('div.article-wrapper ul.article li a')  # 请根据实际页面结构调整选择器

            return [link['href'] for link in news_links]
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return []
    except Exception as e:
        print(f"发生错误：{e}")
        return []


def fetch_news_content(link):
    """根据新闻链接获取新闻内容"""
    if db.pg_db.check_link_exists(link):
        print(f"该链接 {ensure_https_link(link)} 已存在，跳过爬取。")
        return

    time.sleep(random.uniform(1, 3))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(ensure_https_link(link), headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取新闻栏目
            category = soup.find('div', class_='breadnav').find_all('a')[-1].text

            about = soup.find('div', class_='breadnav').find_all('a')[-2].text

            # 获取新闻日期
            date = soup.select_one('div.article-info span.time').text.strip()
            # 定义时间字符串的格式
            time_format = "%Y年%m月%d日 %H:%M"
            release_date = datetime.strptime(date, time_format)

            # 获取新闻标题
            title = soup.select_one('div.article-details h1')
            if title is not None:
                title = title.text.strip()
            else:
                title = ""

            # 提取文章内容
            content_paragraphs = soup.select('div.details p[data-paraid]')
            content = ' '.join([p.get_text(strip=True) for p in content_paragraphs])

            if content == "":
                content_paragraphs = soup.select('div.details p.editor-paragraph span')
                content = ' '.join([p.get_text(strip=True) for p in content_paragraphs])

            if not (title and content):
                print(f"新闻标题和内容 均为空，跳过爬取链接 {ensure_https_link(link)}")
                return

            print(f"栏目：{about} {category}\n标题：{title}\n内容：{content}\n发稿时间：{release_date}\n{'-' * 50}")

            db.pg_db.save_to_db(category,
                                title,
                                content,
                                about,
                                ensure_https_link(link),
                                release_date.year,
                                release_date.month,
                                release_date.day)
        else:
            print(f"访问新闻详情页失败，状态码：{response.status_code} 链接 {ensure_https_link(link)}")

    except Exception as e:
        print(f"访问新闻详情页发生错误：{e} 链接 {ensure_https_link(link)}")


if __name__ == "__main__":
    top_level_url = "https://www.autohome.com.cn/all/"
    category_urls = fetch_category_links(top_level_url)

    if category_urls:
        for category_url in category_urls:
            page_links = fetch_page(category_url)
            if page_links:
                for page_link in page_links:
                    links = fetch_news_links(page_link)
                    if links:
                        for link in links:
                            fetch_news_content(link)
    else:
        print("未找到新闻链接。")

    # page_links = fetch_page("https://www.autohome.com.cn/news/")
    # print('\n'.join(page_links))
    # print(len(page_links))

    # links = fetch_news_links("https://www.autohome.com.cn/news/")
    # print('\n'.join(links))
    # print(len(links))

    # fetch_news_content("https://www.autohome.com.cn/tech/202402/1293441.html#pvareaid=102624")
