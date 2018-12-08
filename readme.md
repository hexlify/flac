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

# Запуск

```
$ cd flac
$ python main.py [-h] file {info,play,covers} ...
```

# Запуск тестов

```
$ pytest .
```