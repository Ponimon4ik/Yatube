# Yatube, новая удобная соцсеть для блогеров

### Описание 
Благодаря этому проекту блогеры смогут опубликовывать свои дневники, а так же читать дневники других блогеров

### Используемые технологии:

+ Python
+ Django
+ CSS
+ Bootstrap
+ SQLite

### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Ponimon4ik/hw05_final
```
```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```
```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

В папке с файлом manage.py выполните команды: 
```
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

### Автор
Стефанюк Богдан
