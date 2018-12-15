# Установка зависимостей

Работает с `python3.5+`

```
$ cat packages | xargs apt-get install -y
$ pip3 install -r requirements.txt
```

# Скачивание тестовых файлов

```
$ chmod +x get_samples.sh
$ ./get_samples.sh
```

# Запуск тестов

```
$ pytest .
```

# Запуск

```
$ python main.py [-h] {meta,play,covers,conv,retr} ...
```

## Команды

+ `meta` - показ метаинформации файла
+ `play` - проигрывание
+ `covers` - извлечение обложек
+ `conv` - конвертация в `.wav`
+ `retr` - печать аудиоданных в консоль