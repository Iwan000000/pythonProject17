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

