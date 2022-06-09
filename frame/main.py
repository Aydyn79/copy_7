from quopri import decodestring

from frame.requests import Post, Get
from patterns.create_pattern import Logger

log = Logger()

class PageNotFound:
    def __call__(self, request):
        return 'Oops, something went wrong.', 'Check if the address is spelled correctly'


class Framework:

    def __init__(self, routes_obj, fronts_obj):
        self.routes = routes_obj
        self.fronts = fronts_obj

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            # конвертируем значения словаря в байты,
            # попутно заменяя знаки
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data

    def __call__(self, env, response):
        # получаем ссылку
        path = env['PATH_INFO']
        # добавляем в конец ссылки слэш, если отсутствует
        path += '/' if path[len(path)-1] != '/' else ''
        request = {}
        # получаем метод запроса
        method_request = env['REQUEST_METHOD']
        # начинаем наполнять словарь запроса данными
        request['method'] = method_request
        if method_request == 'POST':
            data = Post().get_request_params(env)
            request['data'] = Framework.decode_value(data)
            # print(f'Пришли данные с формы на странице Contact us: {Framework.decode_value(data)}')
        if method_request == 'GET':
            request_params = Get().get_request_params(env)
            request['request_params'] = Framework.decode_value(request_params)
            # print(f'Пришли параметры GET-запроса:'
            #       f' {Framework.decode_value(request_params)}')

        # если такой путь существует
        # отработка паттерна page controller
        if path in self.routes:
            view = self.routes[path]
        else:
            view = PageNotFound()

        # наполняем словарь request
        # результатами жизнедеятельности
        # функций add_date, add_key из модуля urls.py
        for item in self.fronts:
            item(request)
        # запуск контроллера с передачей объекта request
        print(request)
        code, body = view(request)
        response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

# Отладочный WSGI-application
class Debuging(Framework):
    def __init__(self, routes, fronts):
        self.application = Framework(routes, fronts)
        super().__init__(routes, fronts)

    def __call__(self, env, start_response):
        print("\033[34m {}" .format("Вы работаете в отладочном режиме"))
        print("\033[33m {}" .format(env))
        # Except error
        if 'error' in env['PATH_INFO'].lower():
            raise Exception('Detect "error" in URL path')

        # Session
        session = env.get('paste.session.factory', lambda: {})()
        if 'count' in session:
            count = session['count']
        else:
            count = 1
        session['count'] = count + 1
        print(f'Вы были здесь {count} раза...')
        return self.application(env, start_response)

# Фейковый WSGI-application.
# О чём и извещает пользователя, впоследствии перенаправляя
# на сайт Роскомнадзора
class FakeApplication(Framework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = Framework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        with open('text.txt', 'r', encoding='utf-8') as infile:
            content = infile.read()
        return [bytes(content, encoding='cp1251')]

