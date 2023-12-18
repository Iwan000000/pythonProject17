import psycopg2
from hhru import get_vacancies, get_employer
from config import config



def create_table(database_neme: str, params: dict):
    """Создание БД, создание таблиц"""

    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {database_neme}")
    cur.execute(f"CREATE DATABASE {database_neme}")

    conn.close()

    conn = psycopg2.connect(dbname=database_neme, **params)

    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE Employers (
                        employer_id INTEGER PRIMARY KEY,
                        company_name VARCHAR(100) NOT NULL,
                        open_vacancies INTEGER
                        )
                        """)
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE Vacancies (
                        vacancy_id SERIAL PRIMARY KEY,
                        employer_id INTEGER REFERENCES Employers(employer_id),
                        vacancies_name VARCHAR(100) NOT NULL,
                        requirement TEXT,
                        payment INTEGER,
                        vacancies_url TEXT,
                        department_name VARCHAR(100)
                        )
                        """)
    conn.commit()
    conn.close()


def add_to_table(employers_list, database_neme: str, params: dict):
    """Заполнение базы данных компании и вакансии"""

    conn = psycopg2.connect(dbname=database_neme, **params)
    with conn.cursor() as cur:
        cur.execute('TRUNCATE TABLE employers, vacancies RESTART IDENTITY;')

        for employer in employers_list:
            employer_list = get_employer(employer)

            cur.execute('INSERT INTO employers (employer_id, company_name, open_vacancies) '
                        'VALUES (%s, %s, %s) RETURNING employer_id',
                        (employer_list['employer_id'], employer_list['company_name'],
                         employer_list['open_vacancies']))

        for employer in employers_list:
            vacancy_list = get_vacancies(employer)
            for v in vacancy_list:
                cur.execute('INSERT INTO vacancies (vacancy_id, vacancies_name, '
                            'payment, requirement, vacancies_url, employer_id, department_name) '
                            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                            (v['vacancy_id'], v['vacancies_name'], v['payment'],
                             v['requirement'], v['vacancies_url'], v['employer_id'], v['department_name']))

    conn.commit()
    conn.close()


class DBManager:
    '''Класс для подключения к БД'''

    def __init__(self, params):
        """
        Инициализация объекта DBManager.
        :param params: Параметры подключения к БД.
        """
        self.conn = psycopg2.connect(dbname="coursework", **params)


    def get_companies_and_vacancies_count(self):
        '''Метод получает список всех компаний и
        количество вакансий у каждой компании'''

        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT company_name, COUNT(vacancies_name) AS count_vacancies  "
                            f"FROM employers "
                            f"JOIN vacancies USING (employer_id) "
                            f"GROUP BY employers.company_name")
                result = cur.fetchall()
            conn.commit()
        return result


    def get_all_vacancies(self):
        '''Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию'''
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT employers.company_name, vacancies.vacancies_name, "
                            f"vacancies.payment, vacancies_url "
                            f"FROM employers "
                            f"JOIN vacancies USING (employer_id)")
                result = cur.fetchall()
            conn.commit()
        return result


    def get_avg_salary(self):
        '''Метод получает среднюю зарплату по вакансиям'''
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT AVG(payment) as avg_payment FROM vacancies ")
                result = cur.fetchall()
            conn.commit()
        return result


    def get_vacancies_with_higher_salary(self):
        '''Метод получает список всех вакансий,
        у которых зарплата выше средней по всем вакансиям'''
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM vacancies "
                            f"WHERE payment > (SELECT AVG(payment) FROM vacancies) ")
                result = cur.fetchall()
            conn.commit()
        return result


    def get_vacancies_with_keyword(self, keyword):
        '''Метод получает список всех вакансий,
        в названии которых содержатся переданные в метод слова'''
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM vacancies "
                            f"WHERE lower(vacancies_name) LIKE '%{keyword}%' "
                            f"OR lower(vacancies_name) LIKE '%{keyword}'"
                            f"OR lower(vacancies_name) LIKE '{keyword}%';")
                result = cur.fetchall()
            conn.commit()
        return result


    def stop(self):
        """
        Закрытие соединения с БД.
        """
        self.conn.close()
        if self.conn.closed:
            print("Соединение закрыто")
        else:
            print("Соединение открыто")

