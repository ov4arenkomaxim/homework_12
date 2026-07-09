import json
import requests

BASE_URL = "http://127.0.0.1:5000"

# текст для запису у results.txt
log_lines = []


def log(text): 
    print(text)
    log_lines.append(text)


def log_response(step_title, response):
    log(f"\n{'=' * 70}")
    log(step_title)
    log(f"{'=' * 70}")
    log(f"Статус-код: {response.status_code}")
    try:
        body = response.json()
        log(f"Тіло відповіді: {json.dumps(body, ensure_ascii=False, indent=2)}")
    except ValueError:
        log(f"Тіло відповіді: {response.text}")


def main():
    # Отримати всіх студентів GET
    resp = requests.get(f"{BASE_URL}/students")
    log_response("GET /students (список усіх студентів, до створення)", resp)

    # Створити трьох студентів POST
    students_to_create = [
        {"first_name": "Іван", "last_name": "Петренко", "age": 20},
        {"first_name": "Олена", "last_name": "Коваленко", "age": 22},
        {"first_name": "Максим", "last_name": "Сидоренко", "age": 21},
    ]

    created_students = []
    for i, student_data in enumerate(students_to_create, start=1):
        resp = requests.post(f"{BASE_URL}/students", json=student_data)
        log_response(f"{i}: POST /students (створення студента {student_data})", resp)
        if resp.status_code == 201:
            created_students.append(resp.json())

    if len(created_students) < 3:
        log("\nне вдалося створити всіх трьох студентів.")
        write_results()
        return

    first_id = created_students[0]["id"]
    second_id = created_students[1]["id"]
    third_id = created_students[2]["id"]

    # отримати інфу про всіх існуючих студентів GET
    resp = requests.get(f"{BASE_URL}/students")
    log_response("GET /students (список усіх студентів, після створення)", resp)

    # Оновити вік другого студента PATCH
    new_age_second = 23
    resp = requests.patch(f"{BASE_URL}/students/{second_id}", json={"age": new_age_second})
    log_response(f"PATCH /students/{second_id} (оновлення віку другого студента на {new_age_second})", resp)

    # Отримати інфу про другого студента GET
    resp = requests.get(f"{BASE_URL}/students/{second_id}")
    log_response(f"GET /students/{second_id} (інформація про другого студента)", resp)

    # Оновити ім'я, прізвище та вік третього студента PUT
    updated_third = {"first_name": "Максим", "last_name": "Гриценко", "age": 25}
    resp = requests.put(f"{BASE_URL}/students/{third_id}", json=updated_third)
    log_response(f"PUT /students/{third_id} (повне оновлення третього студента: {updated_third})", resp)

    # Отримати інформацію про третього студента GET
    resp = requests.get(f"{BASE_URL}/students/{third_id}")
    log_response(f"GET /students/{third_id} (інформація про третього студента)", resp)

    # Отримати всіх студентів GET
    resp = requests.get(f"{BASE_URL}/students")
    log_response("GET /students (список усіх студентів, перед видаленням)", resp)

    # Видалити першого студента DELETE
    resp = requests.delete(f"{BASE_URL}/students/{first_id}")
    log_response(f"DELETE /students/{first_id} (видалення першого студента)", resp)

    # Отримати всіх наявних студентів GET
    resp = requests.get(f"{BASE_URL}/students")
    log_response("GET /students (список усіх студентів, після видалення)", resp)

    write_results()


def write_results():
    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print("\nРезультати збережено у results.txt")


if __name__ == "__main__":
    main()
