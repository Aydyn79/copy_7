from datetime import date
from views import Index, About, Contact_us, CreateService, CreateEquipment, EquipmentList, CopyService, ServicesList


def add_date(request):
    request['date'] = date.today()


def add_key(request):
    request['key'] = '$S$C33783772bRXEx1aCsvY.dqgaaSu76XmVlKrW9Qu8IQlvxHlmzLf'


fronts = [add_date, add_key]
