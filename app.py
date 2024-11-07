import time
import psycopg2
from flask import Flask, request

app = Flask(__name__)

DB_HOST = 'db'
DB_NAME = 'counter_db'
DB_USER = 'user'
DB_PASS = 'password'

# Функция для очистки таблицы hits; после перезапуска контейнера счетчик запоминал значения; опционально можно не использовать
def clear_visits():
    conn = None
    retries = 5
    
    while retries > 0:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            cursor = conn.cursor()
            
            # Удаление всех записей из hits
            cursor.execute("DELETE FROM hits;")
            
            cursor.close()
            conn.commit()
            break
        except Exception as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
        finally:
            if conn is not None:
                conn.close()

# Функция для добавления нового посещения
def log_visit(client_info):
    conn = None
    retries = 5
    
    while retries > 0:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            cursor = conn.cursor()
            
            # Вставляю новую запись о посещении
            cursor.execute("INSERT INTO hits (client_info) VALUES (%s);", (client_info,))
            
            cursor.close()
            conn.commit()
            break
        except Exception as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
        finally:
            if conn is not None:
                conn.close()

# Функция для получения всех посещений
def get_visits():
    conn = None
    visits = []
    retries = 5
    
    while retries > 0:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            cursor = conn.cursor()
            
            # Получаю все записи о посещениях
            cursor.execute("SELECT id, timestamp, client_info FROM hits ORDER BY id DESC;")
            visits = cursor.fetchall()
            
            cursor.close()
            break
        except Exception as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
        finally:
            if conn is not None:
                conn.close()

    return visits

# Функция для подсчета общего количества посещений
def count_visits():
    conn = None
    count = 0
    retries = 5
    
    while retries > 0:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            cursor = conn.cursor()
            
            # Подсчитываю количество записей о посещениях
            cursor.execute("SELECT COUNT(*) FROM hits;")
            count = cursor.fetchone()[0]
            
            cursor.close()
            break
        except Exception as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
        finally:
            if conn is not None:
                conn.close()

    return count

@app.route('/')
def hello():
    client_info = request.headers.get('User-Agent')  # Получаю информацию о клиенте из заголовков запроса
    log_visit(client_info)  # Логирую новое посещение
    
    total_visits = count_visits()  # Получаю общее количество посещений
    return f'Hello World! I have been seen {total_visits} times.\n'

@app.route('/stats')
def stats():
    visits = get_visits()
    
    # Информация о всех посещениях
    stats_info = ''
    
    for visit in visits:
        stats_info += f'ID: {visit[0]}, Timestamp: {visit[1]}, Client Info: {visit[2]}<br>'
    
    if not stats_info:
        return 'No visit data available.<br>'
    
    return stats_info

if __name__ == '__main__':
    clear_visits()  # Очищаю данные перед запуском приложения
    app.run(host='0.0.0.0', debug=True)
