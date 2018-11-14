import logging

import pymysql
from lianjia import settings

MYSQL_HOSTS = settings.MYSQL_HOSTS
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DB


class Sql:
    @classmethod
    def insert(cls, table_name, data_dict):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()

            data_values = "(" + "%s," * (len(data_dict)) + ")"
            data_values = data_values.replace(',)', ')')

            db_field = data_dict.keys()
            data_tuple = tuple(data_dict.values())
            db_field = str(tuple(db_field)).replace("'", '')
            sql = """ insert into %s %s values %s """ % (table_name, db_field, data_values)
            params = data_tuple
            cur.execute(sql, params)
            cnx.commit()
        except Exception as e:
            print(e)
            logging.error(e)
            logging.error(data_dict)
            cnx.rollback()
        finally:
            cnx.close()

    @classmethod
    def select_by_id(cls, table_name, id):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            sql = "select EXISTS(select 1 from %s where id=%%(id)s)" % table_name
            value = {
                'id': id
            }
            cur.execute(sql, value)
            return cur.fetchall()[0]
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    @classmethod
    def select_by_id_date(cls, table_name, id, dt):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            sql = '''select EXISTS(
            select 1 
            from %s 
            where id=%%(id)s and crawl_date=str_to_date(%%(dt)s,'%%%%Y-%%%%m-%%%%d')
            )''' % table_name
            value = {
                'id': id,
                'dt': dt
            }
            cur.execute(sql, value)
            return cur.fetchall()[0]
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    @classmethod
    def get_community_by_area(cls, area):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            arg_len=1
            if type(area) is list:
                arg_len=len(area)
            elif type(area) is str:
                arg_len=1
            arg_list = ','.join(['%s'] * arg_len)
            sql = '''
            select id,name 
            from community 
            where area in (%s)
            order by rand()
            ''' % arg_list
            cur.execute(sql, area)
            return cur.fetchall()
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    @classmethod
    def select_crawl_url(cls, c_type, source, dt):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            sql = ""
            if c_type == "selling_apt":
                sql = '''
    select url 
    from crawl_url cu
    where cu.type="selling_apt" and cu.source=%(source)s and cu.status=0 and crawl_date=str_to_date(%(dt)s,'%%Y-%%m-%%d')
                '''
            value = {
                'source': source,
                'dt':dt
            }
            cur.execute(sql, value)
            return cur.fetchall()
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    @classmethod
    def update_crawl_url_status(cls, status, id, crawl_dt):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()

            sql = """ 
            update crawl_url set status=%(status)s,last_update_time=now()
            where id=%(id)s and to_days(crawl_date)=to_days(%(dt)s)
            """
            params = {
                'status': status,
                'id': id,
                'dt': crawl_dt
            }
            cur.execute(sql, params)
            cnx.commit()
        except Exception as e:
            print(e)
            logging.error(e)
            cnx.rollback()
        finally:
            cnx.close()

    @classmethod
    def get_crawl_url_total_num(cls, source, type, rawurl, crawl_dt):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            sql = '''
        select count(1) 
        from crawl_url
        where source=%(source)s
        and `type`=%(type)s 
        and crawl_date=str_to_date(%(dt)s,'%%Y-%%m-%%d')
        and rawurl=%(rawurl)s 
                    '''
            value = {
                'source': source,
                'type': type,
                'dt': crawl_dt,
                'rawurl': rawurl
            }
            cur.execute(sql, value)
            return cur.fetchall()[0]
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    @classmethod
    def get_crawl_url_total_num2(cls, source, type, rawurl,rawurl2, crawl_dt):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            sql = '''
        select count(1) 
        from crawl_url
        where source=%(source)s
        and `type`=%(type)s 
        and crawl_date=str_to_date(%(dt)s,'%%Y-%%m-%%d')
        and rawurl=%(rawurl)s
        and rawurl2=%(rawurl2)s
                    '''
            value = {
                'source': source,
                'type': type,
                'dt': crawl_dt,
                'rawurl': rawurl,
                'rawurl2': rawurl2
            }
            cur.execute(sql, value)
            return cur.fetchall()[0]
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    @classmethod
    def get_qfang_need_crawl_url(self, rawurl, crawl_dt):
        cnx = pymysql.connect(host=MYSQL_HOSTS, port=int(MYSQL_PORT), user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DB)
        try:
            cur = cnx.cursor()
            sql = '''
            select count(1) ct
from(
            select count(1)
            from crawl_url
            where crawl_date=str_to_date(%(dt)s,'%%Y-%%m-%%d')
            and source='qfang' and rawurl=%(rawurl)s
            group by source,TO_DAYS(crawl_time),rawurl,rawurl2
            having(count(1)<30)
) tmp
                    '''
            value = {
                'dt': crawl_dt,
                'rawurl': rawurl
            }
            cur.execute(sql, value)
            return cur.fetchall()[0]
        except Exception as e:
            print(e)
        finally:
            cnx.close()
