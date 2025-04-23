# Импорт встроенной библиотеки для работы веб-сервера
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import os

# Для начала определим настройки запуска
hostName = "localhost" # Адрес для доступа по сети
serverPort = 8080 # Порт для доступа по сети


class MyServer(BaseHTTPRequestHandler):
    """
        Специальный класс, который отвечает за
        обработку входящих и исходящих запросов от клиентов
    """
    def do_GET(self):
        """Метод для обработки входящих GET-запросов"""
        try:
            # присваивание пути к файлам и типа данных в зависимости от начального пути
            if self.path == '/' or self.path == '/contacts':
                file_path = "../website/contacts.html"
                content_type = 'text/html'
            elif self.path.startswith('/images/'):
                file_path = f"../website{self.path}"
                content_type = 'image/svg+xml' if self.path.endswith('.svg') else 'image/png'
            # обработка пути /favicon.ico
            elif self.path == '/favicon.ico':
                self.send_response(204)  # Нет контента
                self.end_headers()
            else:
                self.send_error(404, "Page Not Found")

            with open(file_path, "rb") as file:
                self.send_response(200)  # Отправка кода ответа
                self.send_header('Content-type', content_type)  # Отправка типа данных, который будет передаваться
                self.end_headers()  # Завершение формирования заголовков ответа
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        """Метод для обработки исходящих POST-запросов"""
        if self.path == '/submit_form':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                form_data = parse_qs(post_data)

                name = form_data.get('name', [''])[0]
                email = form_data.get('email', [''])[0]
                message = form_data.get('message', [''])[0]

                print(f"Получена форма: Имя={name}, Email={email}, Сообщение={message}")

                # Сохранение данных в файл
                os.makedirs("../website/data", exist_ok=True)
                with open("../website/data/form_submissions.txt", "a", encoding="utf-8") as f:
                    f.write(f"Name: {name}, Email: {email}, Message: {message}\n")

                # Перенаправление обратно
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()

            except Exception as e:
                print(f"Ошибка: {str(e)}")
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_error(404, "Page Not Found")

    def serve_file(self, path, content_type, binary=False):
        """Сохранение данных, полученных с помощью POST-запроса"""
        try:
            mode = 'rb' if binary else 'r'
            with open(path, mode) as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                data = file.read()
                if not binary:
                    data = bytes(data, "utf-8")
                self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404, "File Not Found")

if __name__ == "__main__":
    # Инициализация веб-сервера, который будет по заданным параметрах в сети
    # принимать запросы и отправлять их на обработку специальному классу
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        # Старт веб-сервера в бесконечном цикле прослушивания входящих запросов
        webServer.serve_forever()
    except KeyboardInterrupt:
        # Корректный способ остановить сервер в консоли через сочетание клавиш Ctrl + C
        pass

    # Корректная остановка веб-сервера, чтобы он освободил адрес и порт в сети, которые занимал
    webServer.server_close()
    print("Server stopped.")