# Config
Создаём файл local_config.py в этой папке, и прописываем все уникальные настройки. 
В .gitignore специально прописано не добавлять этот файл в коммиты.

```
-- db_init.sql # структура базы данных
-- config.py # базовый конфиг, специфицируем опции в local_config.py
-- get_alphas.py # забирает загруженные в вебсим альфы и складывает их в нужном формате
-- load_to_db.py # получает на вход файлик с альфами, симулирует, сохраняет статы и закидывает в базу данных с флагом submitted=True
-- local_config.py # файл с локальными настройками
```