class Get:

    @staticmethod
    def parse_input_data(data: str):
        if data:
            params = data.split('&')
            return {k: v for item in params for k, v in [item.split('=')]}
        return {}

    @staticmethod
    def get_request_params(environ):
        # получаем строку запроса
        query_string = environ['QUERY_STRING']
        # парсим параметры в словарь
        return Get.parse_input_data(query_string)


# post requests
class Post:

    @staticmethod
    def parse_input_data(data: str):
        if data:
            params = data.split('&')
            return {k: v for item in params for k, v in [item.split('=')]}
        return {}

    @staticmethod
    def get_wsgi_input_data(env) -> bytes:
        # получаем длину тела и приводим к int
        try:
            content_length = int(env.get('CONTENT_LENGTH'))
        except ValueError:
            # если 'CONTENT_LENGTH' пустой, то присваиваем нуль
            content_length = 0

        if content_length:
            return env['wsgi.input'].read(content_length)
        # если нет, то пустая байтовая строка
        return b''

    def parse_wsgi_input_data(self, data: bytes) -> dict:
        if data:
            # декодируем данные, если они есть.
            data_str = data.decode(encoding='utf-8')
            # и выдаём словарь
            return self.parse_input_data(data_str)
        # если нет, то выдаём пустой словарь
        return {}

    def get_request_params(self, environ):
        '''получаем и декодируем параметры'''
        return self.parse_wsgi_input_data(self.get_wsgi_input_data(environ))
