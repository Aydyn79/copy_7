from datetime import datetime
from time import time


class Debug:
    '''
    Декоратор выводит в консоль имя класса и имя метода,
    для метода __call__ тип запроса,
    для остальных методов их аргументы,
    а также выводится время вызова метода
    '''

    def __call__(self, cls):
        # Узнаем имя класса и декорируемой функции
        self.cls_name = cls.__qualname__

        def request_type(method):
            def req(*args, **kw):
                result = method(*args, **kw)
                print(result)
                if method.__name__ == '__call__':
                    print(f'debug --> имя класса.имя функции: {self.cls_name} тип запроса {args[1]["method"]}, время вызова {datetime.now()}')
                else:
                    print(f'debug --> имя класса.имя функции: {self.cls_name} аргументы функции {args}, {kw}, время выполнения {args[1]["date"]}')
                return result
            return req
        return request_type(cls)

# Думал как улучшить или изменить данный декоратор,
# но он настолько лаконично сделан, что тут ни убавить, не прибавить.
class AppRoute:
    def __init__(self, routes, url):
        '''
        Инициируем значения параметров
        '''
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        '''
        Cвязываем URL c объектом декорируемого класса
        '''
        self.routes[self.url] = cls()


