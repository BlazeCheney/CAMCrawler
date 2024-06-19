from datetime import datetime

import requests
from bs4 import BeautifulSoup

from common.link_check import ensure_https_link


def fetch_page(url):
    print(f"新闻栏目 {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.1.1 Safari/537.36'
    }
    try:
        response = requests.get(ensure_https_link(url), headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')

        pages = soup.select('div.pcauto_page a')

        lastpage = pages[-2].text.strip()

        return [f"{url}/index_{num}.html" for num in range(1, int(lastpage) + 1)]

    except requests.RequestException as e:
        print(f"请求出错：{e}")
    return []


def fetch_news_link(url):
    print(f"新闻列表 {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.1.0.1 Safari/537.36'
    }
    try:
        response = requests.get(ensure_https_link(url), headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        news_links = soup.select('p.tit a')

        guide = soup.select('div.guide span.mark a')
        about = ''
        category = ''
        if guide:
            about_tag = guide[-2].text.strip()
            if about_tag:
                about = about_tag.encode('utf-8', errors='replace').decode('utf-8',errors='replace')
            category_tag = guide[-1].text.strip()
            if category_tag:
                category = category_tag.encode('utf-8', errors='replace').decode('utf-8',errors='replace')

        return [link['href'] for link in news_links if link.has_attr('href')], about, category
    except requests.RequestException as e:
        print(f"请求出错：{e}")
    return [], '', ''


def fetch_news_content(link, about, category):
    # time.sleep(random.uniform(1, 3))
    link = ensure_https_link(link)
    print(f'文章链接 {link}')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.1.0.1 Safari/537.36'
    }
    try:
        response = requests.get(link, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('h1', class_='tit')
        title = title_tag.text.strip() if title_tag else ''
        title = title.encode('latin1', errors='replace').decode('utf-8', errors='replace')

        date = soup.select_one('span.pubTime').text.strip()
        # 定义时间字符串的格式
        time_format = "%Y-%m-%d %H:%M:%S"
        release_date = datetime.strptime(date, time_format)

        content_tag = soup.select('div.artText p')
        content = ''
        if content_tag:
            for c in content_tag:
                text = c.text.strip()
                if text:
                    content += text.encode('latin1', errors='replace').decode('utf-8', errors='replace')

        print(f"栏目：{about} {category}\n标题：{title}\n内容：{content}\n发稿时间：{release_date}\n{'-' * 50}")
    except requests.RequestException as e:
        print(f"请求出错：{e} 链接 {link}")


if __name__ == "__main__":
    base_url = 'https://www.pcauto.com.cn'

    category_urls = [f'{base_url}/nation/gckx/',
                     f'{base_url}/nation/jkkx/',
                     f'{base_url}/nation/gwkx/',
                     f'{base_url}/nation/ycxc/']

    if category_urls:
        for category_url in category_urls:
            page_urls = fetch_page(category_url)
            if page_urls:
                for page_url in page_urls:
                    news_links, about, category = fetch_news_link(page_url)
                    if news_links:
                        for link in news_links:
                            fetch_news_content(link, about, category)
