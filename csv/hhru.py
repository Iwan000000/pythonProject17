import requests
import psycopg2

def get_vacancies(employer_id):
    """Получение данных вакансий по API"""

    params = {
        'area': 2,
        'page': 0,
        'per_page': 10
    }
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}"
    data_vacancies = requests.get(url, params=params).json()


    vacancies_data = []
    for item in data_vacancies["items"]:
        department_name = None
        if item['department']:
            department_name = item['department']['name']
        hh_vacancy = {
            'vacancy_id': int(item['id']),
            'vacancies_name': item['name'],
            'payment': item["salary"]["from"] if item.get("salary") else None,
            'requirement': item['snippet']['requirement'],
            'vacancies_url': item['alternate_url'],
            'department_name': department_name,
            'employer_id': item['employer']['id'],
        }
        vacancies_data.append(hh_vacancy)

    return vacancies_data

def get_employer(employer_id):
    """Получение данных о работодателях по API"""

    url = f"https://api.hh.ru/employers/{employer_id}"
    data_employer = requests.get(url).json()
    hh_employer = {
        'employer_id': int(employer_id),
        'company_name': data_employer.get('name'),
        'open_vacancies': data_employer.get('open_vacancies'),
        'employer_url': data_employer.get('alternate_url')
    }
    return hh_employer


def create_table():
    """Создание БД, создание таблиц"""

    conn = psycopg2.connect(host="localhost", database="postgres",
                            user="postgres", password="1379")
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("DROP DATABASE IF EXISTS course_work_5")
    cur.execute("CREATE DATABASE course_work_5")

    conn.close()

    conn = psycopg2.connect(host="localhost", database="course_work_5",
                            user="postgres", password="1379")
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE Employers (
                        employer_id INTEGER PRIMARY KEY,
                        company_name VARCHAR(100) NOT NULL,
                        open_vacancies INTEGER)
                        """)

        cur.execute("""
                    CREATE TABLE Vacancies (
                        vacancy_id SERIAL PRIMARY KEY,
                        employer_id INTEGER REFERENCES Employers(employer_id),
                        vacancies_name VARCHAR(100) NOT NULL,
                        requirement TEXT,
                        payment INTEGER,
                        vacancies_url TEXT,
                        department_name VARCHAR(100))
                        """)
    conn.commit()
    conn.close()


def add_to_table(employers_list):
    """Заполнение базы данных компании и вакансии"""

    with psycopg2.connect(host="localhost", database="course_work_5",
                          user="postgres", password="1379") as conn:
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
