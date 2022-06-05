from threading import local
# from patterns.create_pattern import Mappers

# UoW pattern
'''
Работает с базой данных, осуществляет операции вставки, изменения, удаления записей.
Использует класс Mappers из модуля pattern.create_pattern, который является слоем между 
движком приложения Engine и классом UnitOfWork
'''
class UnitOfWork:
    """
    UoW pattern
    """
    # Создаем локальный поток
    current = local()

    def __init__(self):
        self.new_objects = []
        self.modified_objects = []
        self.removed_objects = []

    def set_mapper_registry(self, Mappers):
        self.Mappers = Mappers

    def register_new(self, obj):
        self.new_objects.append(obj)

    def register_modified(self, obj):
        self.modified_objects.append(obj)

    def register_removed(self, obj):
        self.removed_objects.append(obj)

    def commit(self):
        self.insert_new()
        self.update_modified()
        self.delete_removed()

        self.new_objects.clear()
        self.modified_objects.clear()
        self.removed_objects.clear()

    def insert_new(self):
        print(self.new_objects)
        for obj in self.new_objects:
            print(f"Вывожу {self.Mappers}")
            self.Mappers.get_mapper(obj).insert(obj)

    def update_modified(self):
        for obj in self.modified_objects:
            self.Mappers.get_mapper(obj).update(obj)

    def delete_removed(self):
        for obj in self.removed_objects:
            self.Mappers.get_mapper(obj).delete(obj)

    @staticmethod
    def new_current():
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:

    def mark_new(self):
        UnitOfWork.get_current().register_new(self)

    def mark_modified(self):
        UnitOfWork.get_current().register_modified(self)

    def mark_removed(self):
        UnitOfWork.get_current().register_removed(self)
