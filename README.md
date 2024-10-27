# tg_bot_template

*Шаблон для создания ботов*

описание структуры бота
перечень базовых команд



---

## Описание структуры

📁 config_data             - Пакет для хранения файлов с конфигурационными данными
📁 errors                  - Пакет с модулями для обработки исключений, возникающих в процессе работы бота
📁 external_services       - Пакет с модулями для работы с API внешних сервисов
📁 filters                 - Пакет с кастомными фильтрами
📁 handlers                - Пакет, в котором хранятся обработчики апдейтов
📁 keyboards               - Пакет с модулями, в которых хранятся клавиатуры
📁 lexicon                 - Пакет для хранения текстов - ответов бота
📁 middlewares             - Пакет, в котором хранятся мидлвари
📁 datebase                - Пакет с модулями для взаимодействия с базой данных
📁 services                - Пакет с модулями для реализации какой-то бизнес-логики бота
📁 states                  - Пакет с модулями, в которых описаны классы, отражающими возможные состояния пользователей, FSM
📁 tests                   - Пакет с тестами для тестирования работы бота
📁 utils                   - Пакет для хранения вспомогательных модулей, которые нужны в процессе работы бота

---

## Команды для терминала

python -m venv venv                        -  создать папку venv с виртуальным окружением

venv\Scripts\activate                      -  запустить виртуальное окружение для Windows
source venv/Scripts/activate               -  запустить виртуальное окружение для GitBash
deactivate                                 -  выйти из вируального окружения

python --version                           -  проверить версию python
pip --version                              -  проверить версию pip

pip install -r requirements.txt            -  устанвливаем необходимые расширения из requirements (в venv)

pip freeze > requirements.txt              -  сформировать файл requirements


sudo apt update && sudo apt dist-upgrade   -  обновляем и установливаем необходимые пакеты
sudo apt install redis                     -  установка Redis по инструкции для Linux

pip list


git --version
git init
git pull
git add .
git commit -m "text comit"
git push


docker --version
docker

---