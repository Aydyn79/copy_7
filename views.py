from frame.templator import render
from patterns.behav_pattern import ListView, CreateView, BaseSerializer, EmailNotifier, SmsNotifier
from patterns.create_pattern import Engine, Logger, Mappers
from patterns.struct_pattern import Debug, AppRoute
from patterns.uow_pattern import UnitOfWork

log = Logger()
site = Engine()
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(Mappers)

routes = {}

@AppRoute(routes, '/')
class Index:
    @Debug()
    def __call__(self, request):
        print(request)
        return '200 OK', render('index.html', objects_list=site.equipments, date=request.get('date', None))

@AppRoute(routes=routes, url='/about/')
class About:
    @Debug()
    def __call__(self, request):
        return '200 OK', render('page.html', date=request.get('date', None))

@AppRoute(routes=routes, url='/contacts/')
class Contact_us:
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))

# контроллер - список сервисов
@AppRoute(routes=routes, url='/service_list/')
class ServicesList:
    def __call__(self, request):
        log.log('Список видов сервисов')
        try:
            equipment = site.find_equipment_by_id(
                int(request['request_params']['id']))

            return '200 OK', render('service_list.html',
                                    objects_list=equipment.services,
                                    name=equipment.name, id=equipment.id)
        except KeyError:
            return '200 OK', 'Ни одного сервиса еще не добавлено'


# контроллер создания сервиса
@AppRoute(routes=routes, url='/create_service/')
class CreateService:
    equipment_id = -1
    @Debug()
    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            log.log(name)
            equipment = None
            if self.equipment_id != -1:
                equipment = site.find_equipment_by_id(int(self.equipment_id))
                service = site.create_service('remote_support', name, equipment)
                service.observers.append(email_notifier)
                service.observers.append(sms_notifier)
                site.services.append(service)

            return '200 OK', render('service_list.html',
                                    objects_list=equipment.services,
                                    name=equipment.name,
                                    id=equipment.id)

        else:
            try:
                self.equipment_id = int(request['request_params']['id'])
                equipment = site.find_equipment_by_id(int(self.equipment_id))

                return '200 OK', render('create_service.html',
                                        name=equipment.name,
                                        id=equipment.id)
            except KeyError:
                return '200 OK', 'Пока не добавлено никакого оборудования'


# контроллер создания категории
# ИЗМЕНИЛ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@AppRoute(routes=routes, url='/create_equipment/')
class CreateEquipment:
    @Debug()
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            equipment_id = data.get('equipment_id')
            log.log(equipment_id)
            equipment = None
            if equipment_id:
                equipment = site.find_equipment_by_id(int(equipment_id))
            new_equipment = site.create_equipment(name, equipment)
            log.log(new_equipment.name)
            log.log(new_equipment.services)
            # Внёс изменения
            #=======================================================================
            new_equipment.mark_new()
            UnitOfWork.get_current().commit()
            #=======================================================================
            # Добавил
            # ===================================================================
            mapper = Mappers.get_current_mapper('equipment')
            new_equipment_with_id = mapper.find_by_name(name)
            print(f'новый объект оборудования {new_equipment_with_id.name}')
            print(f'новый объект оборудования {new_equipment_with_id.services}')
            site.equipments.append(new_equipment_with_id)
            # ===================================================================

            return '200 OK', render('index.html', objects_list=site.equipments)
        else:
            equipments = site.equipments
            return '200 OK', render('create_equipment.html',
                                    equipments=equipments)



# контроллер списка оборудования
@AppRoute(routes=routes, url='/equipment_list/')
class EquipmentList:
    @Debug()
    def __call__(self, request):
        print(site.equipments)
        return '200 OK', render('equipment_list.html',
                                objects_list=site.equipments)

    def show_list(self):
        for item in site.equipments:
            print(item.services_count())


# контроллер копирования сервиса
@AppRoute(routes=routes, url='/copy_service/')
class CopyService:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_service = site.get_service(name)
            if old_service:
                new_name = f'copy_{name}'
                new_service = old_service.clone()
                new_service.name = new_name
                site.services.append(new_service)

            return '200 OK', render('service_list.html',
                                    objects_list=site.services,
                                    name=new_service.equipment.name)
        except KeyError:
            return '200 OK', 'Ни одного сервиса еще не добавлено'
#      _________________________________________________________________________________________     #
#  Здесь жил непеределанный код!!!


# Изменил!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@AppRoute(routes=routes, url='/customer_list/')
class CustomerListView(ListView):
    #queryset = site.customers # Убираю, и меняю на get_queryset(self)
    template_name = 'customer_list.html'
    
    #Добавил
    #===================================================================
    def get_queryset(self):
        mapper = Mappers.get_current_mapper('customer')
        return mapper.all()
    #===================================================================
    
    
@AppRoute(routes=routes, url='/customer_create/')
class CustomerCreateView(CreateView):
    template_name = 'create_customer.html'

    def create_obj(self, data):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('customer', name)
        print(new_obj.name)
        site.customers.append(new_obj)
        #Добавил
        #===================================================================
        new_obj.mark_new()
        UnitOfWork.get_current().commit()
        #===================================================================

@AppRoute(routes=routes, url='/add_service/')
class AddServiceByCustomerCreateView(CreateView):
    template_name = 'add_service.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['services'] = site.services
        context['customers'] = site.customers
        return context

    def create_obj(self, data: dict):
        service_name = site.decode_value(data['service_name'])
        service = site.get_service(service_name)
        customer_name = site.decode_value(data['customer_name'])
        customer = site.get_customer(customer_name)
        service.add_customer(customer)


@AppRoute(routes=routes, url='/api/')
class ServiceApi:
    @Debug()
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.services).save()

if __name__ == '__main__':
    mapper = Mappers.get_current_mapper('equipment')
    # for item in mapper.all():
    #     print(item.id)
    # bs = BaseSerializer(mapper.find_by_name('ЧРП'))
    print(mapper.find_by_name('ЧРП').services)
    # print(bs.save())
