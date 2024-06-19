import psycopg2

def check_link_exists(url):
    conn_str = "host=172.16.11.40 port=5432 dbname=python user=cam_dev password=cam_dev@2023"
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()

    # 查询URL是否已存在
    query = "SELECT COUNT(*) FROM news WHERE url = %s;"
    cursor.execute(query, (url,))

    # 获取查询结果
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    # 如果结果大于0，说明URL已存在
    return result > 0

def save_to_db(name, title, body, about, url, year, month, day):
    """
    将爬取的数据保存到PostgreSQL数据库的news表中。
    """
    conn_str = "host=172.16.11.40 port=5432 dbname=python user=cam_dev password=cam_dev@2023"
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()

    # 准备SQL插入语句
    insert_query = """
    INSERT INTO news (name,title, body, about, url,year,month,day)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    # 执行插入操作
    try:
        cursor.execute(insert_query, (name, title, body, about, url, year, month, day))
        conn.commit()
        print(f"数据记录已成功保存至数据库：news")
    except Exception as e:
        print(f"保存数据时发生错误：{e}")
        conn.rollback()  # 发生错误时回滚事务
    finally:
        cursor.close()
        conn.close()
