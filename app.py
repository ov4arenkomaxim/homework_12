#GET/students  = список всіх студентів
#GET/students/<id> = студент за ID
#GET/students?last_name=.. = студенти за прізвищем
#POST/students = створити нового студента
#PUT    /students/<id> = повністю оновити студента
#PATCH  /students/<id> = оновити вік студента
#DELETE /students/<id> = видалити студента

import csv
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.csv")
FIELDNAMES = ["id", "first_name", "last_name", "age"]

# Поля, які дозволено передавати для POST і PUT 
REQUIRED_FIELDS = {"first_name", "last_name", "age"}

#csv-файл
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def read_students():
    init_csv()
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        students = list(reader)
    # приводимо id та age до int для зручності
    for s in students:
        s["id"] = int(s["id"])
        s["age"] = int(s["age"])
    return students


def write_students(students):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for s in students:
            writer.writerow(s)


def get_next_id(students):
    if not students:
        return 1
    return max(s["id"] for s in students) + 1


def find_student_by_id(students, student_id):
    for s in students:
        if s["id"] == student_id:
            return s
    return None

# GET
@app.route("/students", methods=["GET"])
def get_students():
   # Без параметрів   > список усіх студентів.
#?last_name=Прізвище > студент з відповідним прізвищем.
    students = read_students()

    last_name = request.args.get("last_name")
    if last_name is not None:
        matches = [s for s in students if s["last_name"] == last_name]
        if not matches:
            return jsonify({
                "error": f"Студента з прізвищем '{last_name}' не знайдено"
            }), 404
        return jsonify(matches), 200

    return jsonify(students), 200

@app.route("/students/<int:student_id>", methods=["GET"])
def get_student_by_id(student_id):
    students = read_students()
    student = find_student_by_id(students, student_id)
    if student is None:
        return jsonify({
            "error": f"Студента з ID {student_id} не знайдено"
        }), 404
    return jsonify(student), 200


# POST
@app.route("/students", methods=["POST"])
def create_student():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "Тіло запиту не містить жодного поля"}), 400

    body_fields = set(body.keys())

    # помилка про неправильні поля у тілі запиту
    unknown_fields = body_fields - REQUIRED_FIELDS
    if unknown_fields:
        return jsonify({
            "error": f"Передано неіснуючі поля: {', '.join(unknown_fields)}"
        }), 400

    # відсутні поля
    missing_fields = REQUIRED_FIELDS - body_fields
    if missing_fields:
        return jsonify({
            "error": f"Відсутні обов'язкові поля: {', '.join(missing_fields)}"
        }), 400

    try:
        age = int(body["age"])
    except (ValueError, TypeError):
        return jsonify({"error": "Поле age повинно бути числом, годі дурака валяти"}), 400

    students = read_students()
    new_student = {
        "id": get_next_id(students),
        "first_name": str(body["first_name"]),
        "last_name": str(body["last_name"]),
        "age": age,
    }
    students.append(new_student)
    write_students(students)

    return jsonify(new_student), 201

# PUT
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student_put(student_id):
    students = read_students()
    student = find_student_by_id(students, student_id)
    if student is None:
        return jsonify({
            "error": f"Студента з ID {student_id} не знайдено"
        }), 404

    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Тіло запиту не містить жодного поля"}), 400

    body_fields = set(body.keys())

    unknown_fields = body_fields - REQUIRED_FIELDS
    if unknown_fields:
        return jsonify({
            "error": f"Передано неіснуючі поля: {', '.join(unknown_fields)}"
        }), 400

    missing_fields = REQUIRED_FIELDS - body_fields
    if missing_fields:
        return jsonify({
            "error": f"Відсутні обов'язкові поля: {', '.join(missing_fields)}"
        }), 400

    try:
        age = int(body["age"])
    except (ValueError, TypeError):
        return jsonify({"error": "Поле 'age' повинно бути числом"}), 400

    student["first_name"] = str(body["first_name"])
    student["last_name"] = str(body["last_name"])
    student["age"] = age

    write_students(students)
    return jsonify(student), 200

# PATCH
@app.route("/students/<int:student_id>", methods=["PATCH"])
def update_student_patch(student_id):
    students = read_students()
    student = find_student_by_id(students, student_id)
    if student is None:
        return jsonify({
            "error": f"Студента з ID {student_id} не знайдено"
        }), 404

    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Тіло запиту не містить жодного поля"}), 400

    body_fields = set(body.keys())

    # PATCH оновлює лише поле age
    unknown_fields = body_fields - {"age"}
    if unknown_fields:
        return jsonify({
            "error": f"Передано неіснуючі поля: {', '.join(unknown_fields)}"
        }), 400

    if "age" not in body_fields:
        return jsonify({"error": "Відсутнє обов'язкове поле: age"}), 400

    try:
        age = int(body["age"])
    except (ValueError, TypeError):
        return jsonify({"error": "Поле age повинно бути числом"}), 400

    student["age"] = age
    write_students(students)
    return jsonify(student), 200

# DELETE
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    students = read_students()
    student = find_student_by_id(students, student_id)
    if student is None:
        return jsonify({
            "error": f"Студента з ID {student_id} не знайдено"
        }), 404

    students = [s for s in students if s["id"] != student_id]
    write_students(students)

    return jsonify({
        "message": f"Студента з ID {student_id} успішно видалено"
    }), 200


if __name__ == "__main__":
    init_csv()
    app.run(host="0.0.0.0", port=5000, debug=False)
