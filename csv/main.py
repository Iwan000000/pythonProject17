from DBManager import DBManager, create_table, add_to_table
from hhru import get_vacancies, get_employer
from config import config

def main():
    employers_list = [1740,1455, 15478, 8620, 3529, 4006, 4504679, 561525, 4181, 4608157]

    params = config()

    create_table("coursework", params)
    add_to_table(employers_list, "coursework", params)
    dbmanager = DBManager(params)


    while True:

        task = input(
            "Введите 1, чтобы получить список всех компаний и количество вакансий у каждой компании\n"
            "Введите 2, чтобы получить список всех вакансий с указанием названия компании, "
            "названия вакансии и зарплаты и ссылки на вакансию\n"
            "Введите 3, чтобы получить среднюю зарплату по вакансиям\n"
            "Введите 4, чтобы получить список всех вакансий, у которых зарплата выше средней по всем вакансиям\n"
            "Введите 5, чтобы получить список всех вакансий, в названии которых содержатся переданные в метод слова\n"
            "Введите стоп, чтобы завершить работу\n"
        )

        if task.lower() == "стоп":
            print(dbmanager.stop())
            break
        elif task == '1':
            print(dbmanager.get_companies_and_vacancies_count())
            print()
        elif task == '2':
            print(dbmanager.get_all_vacancies())
            print()
        elif task == '3':
            print(dbmanager.get_avg_salary())
            print()
        elif task == '4':
            print(dbmanager.get_vacancies_with_higher_salary())
            print()
        elif task == '5':
            keyword = input('Введите ключевое слово: ')
            print(dbmanager.get_vacancies_with_keyword(keyword))
            print()
        else:
            print('Неправильный запрос')


if __name__ == '__main__':
    main()