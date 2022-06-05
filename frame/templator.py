from jinja2 import Template, FileSystemLoader, Environment
from os.path import join


def render(template_name, folder='templates', **kwargs):
    """
    template_name - имя шаблона
    folder - папка в которой должны лежать шаблоны
    kwargs - прочие аргументы
    """
    # Загружаем папку
    file_loader = FileSystemLoader(folder)
    env = Environment(loader=file_loader)
    #Заряжаем шаблон
    template = env.get_template(template_name)
    #выстреливаем шаблон с параметрами
    return template.render(**kwargs)