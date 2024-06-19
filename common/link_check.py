from urllib.parse import urlparse, urlunparse


def ensure_https_link(link):
    """确保链接以https开头，如果不是则转换之"""
    parsed_link = urlparse(link)
    # 如果没有scheme（即协议部分），或者scheme不是https，则默认使用https
    scheme = parsed_link.scheme if parsed_link.scheme and parsed_link.scheme == 'https' else 'https'
    netloc = parsed_link.netloc
    path = parsed_link.path
    params = parsed_link.params
    query = parsed_link.query
    fragment = parsed_link.fragment

    # 重新组合URL，确保使用https
    return urlunparse((scheme, netloc, path, params, query, fragment))
