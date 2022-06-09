
import os
import sys
from copy import deepcopy

from datetime import datetime
from quopri import decodestring


from sqlite3 import connect
from patterns.behav_pattern import Subject, BaseSerializer
from patterns.uow_pattern import DomainObject



class UnnamedSingleForLogger(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(UnnamedSingleForLogger, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=UnnamedSingleForLogger):
    @staticmethod
    def log(text):
        # Прописываем путь лог-файла
        PATH = os.path.dirname(os.path.abspath(__file__))
        PATH = os.path.join(PATH, 'views.log')
        # Сохраняем текущий стандартный вывод,
        # чтобы можно было вернуть sys.stdout после завершения перенаправления
        stdout_fileno = sys.stdout
        # Направляем вывод sys.stdout в лог-файл
        sys.stdout = open(PATH, 'a', encoding="utf-8")
        # Печатаем в лог-файле текст лога
        sys.stdout.write(f"{datetime.now().strftime('%H:%M:%S - %d.%m.%Y ')} {text} \n")
        # Выводим текст лога на фактический сохраненный обработчик
        stdout_fileno.write(f"{datetime.now().strftime('%H:%M:%S - %d.%m.%Y ')} {text} \n")
        # Закрываем файл
        sys.stdout.close()
        # Восстанавливаем sys.stdout в наш старый сохраненный обработчик файлов
        sys.stdout = stdout_fileno




class AbsUser:
    def __init__(self, name):
        self.name = name


# Заказчик
class Customer(AbsUser, DomainObject):
    def __init__(self, name):
        self.equipments = []
        self.services = []
        super().__init__(name)


# Партнёр компании
class Partner(AbsUser):
    def __init__(self, name):
        self.equipments = []
        self.services = []
        super().__init__(name)


class UserFactory:
    types = {
        'customer': Customer,
        'partner': Partner
    }

    # Фабричный метод
    @classmethod
    def create(cls, role, name):
        return cls.types[role](name)


# порождающий паттерн Прототип
class ServicePrototype:
    # прототип вида оборудования

    def clone(self):
        return deepcopy(self)

# вид оборудования
class Service(ServicePrototype, Subject):

    def __init__(self, name, equipment):
        self.name = name
        self.equipment = equipment
        self.equipment.services.append(self)
        self.customers = []
        super().__init__()

    def __getitem__(self, item):
        return self.customers[item]

    def add_customer(self, customer: Customer):
        self.customers.append(customer)
        customer.services.append(self)
        self.notify()

# Удаленное тех.сопровождение (диагностика, программирование, администрирование и др.)
class RemoteTechnicalSupport(Service):
    pass

# Работы проводимые по месту(ТО, ТР, СМР, ПНР и т.п.)
class TechnicalMaintenance(Service):
    pass



# фабрика сервисов
class ServiceFactory:
    types = {
        'remote_support': RemoteTechnicalSupport,
        'on_site_maintenance': TechnicalMaintenance,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, equipment):
        return cls.types[type_](name, equipment)

# Оборудование
class Equipment(DomainObject):
    auto_id = 0

    def __init__(self, name, equipment=None):
        self.id = Equipment.auto_id
        Equipment.auto_id += 1
        self.name = name
        self.equipment = equipment
        self.services = []

    def services_count(self):
        result = len(self.services)
        if self.equipment:
            print('attention')
            print(self.equipment)
            result += self.equipment.services_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.customers = []
        self.partners = []
        self.services = []
        self.equipments = []

    @staticmethod
    def create_user(role, name):
        return UserFactory.create(role, name)

    @staticmethod
    def create_equipment(name, equipment=None):
        return Equipment(name, equipment)

    def find_equipment_by_id(self, id):
        for item in self.equipments:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_service(type_, name, equipment):
        return ServiceFactory.create(type_, name, equipment)

    def get_service(self, name):
        for item in self.services:
            if item.name == name:
                return item
        return None

    def get_customer(self, name) -> Customer:
        for item in self.customers:
            if item.name == name:
                return item

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')





# Решил создать общий класс AbcMapper, чтобы не повторять часть кода в подклассах
class AbcMapper:
    def __init__(self, connection, tablename):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = tablename
    # Код привязанный к конкретным объектам у нас только в методах all и find_by_id
    def all(self):
        pass

    def find_by_id(self, id):
        pass

    #Only для категории Equipment
    def find_by_name(self, name):
        pass


    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)
            
class CustomerMapper(AbcMapper):

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            customer = Customer(name)
            customer.id = id
            result.append(customer)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Customer(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

class EquipmentMapper(AbcMapper):
    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (id, name, equipObj) VALUES (?,?,?)"
        bs = BaseSerializer(obj)
        equipObj = bs.save()
        self.cursor.execute(statement, (obj.id, obj.name, equipObj))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            _, _, equipObj = item
            result.append(BaseSerializer.load(equipObj))
        return result

    def find_by_id(self, id):
        statement = f"SELECT equipObj FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()[0]
        if result:
            return BaseSerializer.load(result)
            # return result
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def find_by_name(self, name):
        statement = f"SELECT equipObj FROM {self.tablename} WHERE name=?"
        self.cursor.execute(statement, (name,))
        result = self.cursor.fetchone()[0]
        if result:
            return BaseSerializer.load(result)
            # return result
        else:
            raise RecordNotFoundException(f'record with name={name} not found')

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, equipObj=? WHERE id=?"
        bs = BaseSerializer(obj)
        equipObj = bs.save()
        self.cursor.execute(statement, (obj.name, equipObj, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

connection = connect('patterns.sqlite')

# архитектурный системный паттерн - Data Mapper
class Mappers:
    mappers = {
        'customer': CustomerMapper,
        'equipment': EquipmentMapper
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Customer):
            return CustomerMapper(connection, 'customer')
            
        elif isinstance(obj, Equipment):
            return EquipmentMapper(connection, 'equipment')
    
    @staticmethod
    def get_current_mapper(name):
        return Mappers.mappers[name](connection, name)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')



if __name__ == '__main__':
    conn = connect('/home/nexter/PycharmProjects/patterns/patrn_lesson_7/patterns.sqlite')
    mapper = EquipmentMapper(conn, 'equipment')
    mapper1 = CustomerMapper(conn, 'customer')
    resultid = mapper.find_by_id('2')
    # print(resultid.name)
    resultname = mapper.find_by_name('Электродвигатель')
    mapper.update(resultid)
    result = mapper.all()
    for item in result:
        print(item.name)
    print(resultname.id)
    print(resultid.name)


















