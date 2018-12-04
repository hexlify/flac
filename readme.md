# Установка зависимостей

Работает с `python3.5`

```
    sudo apt-get install ffmpeg

    sudo apt-get install libasound-dev
    sudo apt-get install portaudio19-dev
    sudo apt-get install python3.5-dev  # for python3.5

    pip install -r requests.txt
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