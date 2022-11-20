# Соцсеть Yatube

### Описание
Социальная сеть блогеров. Даёт возможность писать посты и публиковать их в отдельных группах, подписываться на любимых блогеров, удалять и комментировать записи.

### Инструкции по установке
- Клонируйте репозиторий:

git clone git@github.com:LanaRemenyuk/yatube_final.git
- Установите и активируйте виртуальное окружение:

для MacOS
python3 -m venv venv
для Windows
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
- Установите зависимости из файла requirements.txt:

pip install -r requirements.txt
- Примените миграции:

python manage.py migrate
- В папке с файлом manage.py выполните команду:

python manage.py runserver

### Автор
Светлана Ременюк
