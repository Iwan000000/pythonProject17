import requests
from abc import ABC, abstractmethod

class BasicClass(ABC):
    @abstractmethod
    def my_method(self):
        pass

LINK = 'https://api.hh.ru/vacancies'

class HH_API(BasicClass):
    """Класс для скрайбинга сайта HH
    возвращает список вакансий
    вакансия в формате JSON"""

    def my_method(self):
        # Реализация абстрактного метода
        pass

    def get_request(self, count, company_name=None):
        """
        Отправляет запрос на API HH и возвращает список вакансий.

        :param keyword: Ключевое слово для поиска вакансий.
        :param count: Количество вакансий для получения.
        :param company_name: Название компании для фильтрации вакансий (по умолчанию None).
        :return: Список вакансий в формате JSON.
        """
        pages = int(count / 20)  # Расчет количества страниц
        params = {
            'page': 0,
            'per_page': 20
        }
        if company_name:
            params['employer_name'] = company_name
        data = []
        for page in range(pages):
            params['page'] = page
            response = requests.get(LINK, params=params)
            if response.status_code == 200:  # Проверка успешности выполнения запроса
                data += response.json()['items']
            else:
                print(f"Ошибка при выполнении запроса. Статус код: {response.status_code}")

        return data

def hh_vacancy():
    hh = HH_API()
    hh_vacancies = hh.get_request(count=20)
    companies = [item['employer']['name'] for item in hh_vacancies[:10]]
    return hh_vacancies[:10], companies

vacancies, companies = hh_vacancy()

for company in companies:
    print(f"Компания:\n{company}\n")
    hh = HH_API()
    hh_vacancies = hh.get_request(count=20, company_name=company)
    for vacancy in hh_vacancies[:10]:
        print(f"вакансии:\n{vacancy}\n")
    print()




