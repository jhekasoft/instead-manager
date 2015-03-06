Instead Manager
===============

Сейчас здесь собрана информация как по использованию менеджера, так и описание для разработчиков. Вероятно в будущем
надо будет изменить структуру. :)

**manager.py** — базовый модуль с реализацией функционала менеджера.

**instead-manager.py** — CLI-реализация.

**instead-manager-tk.pyw** — GUI-реализация с использованием tkinter.

## manager.py

В этом файле находится абстрактный класс `InsteadManager` с базовой реализацией всех возможностей, а также классы
наследники для различных операционных системы: `InsteadManagerFreeUnix` (GNU/Linux, FreeBSD, ...),
`InsteadManagerWin` (Windows), `InsteadManagerMac` (MacOS X). Эти классы дополнены специфичным кодом, который
различается для операционных систем.

## CLI (instead-manager.py)

Реализация command line interface.

![alt text](https://github.com/jhekasoft/instead-manager/raw/master/docs/images/instead-manager-cli.png "instead-manager CLI")

### Использование:

```
python3 instead-manager.py [параметры]
```

или (с правами на исполнение)

```
./instead-manager.py [параметры]
```

В системе Windows примерно так:

```
C:\Python34\python.exe instead-manager.py [параметры]
```

Если же менеджер будет у вас установлен в системе, то скорее всего его можно будет использовать с помощью такой
команды:

```
instead-manager [параметры]
```

### Примеры использования:

Далее в примерах будет использоваться самый простой вариант.

Список возможных параметров можно посмотреть с помощью атрибута -h:

```
./instead-manager.py -h
```

Обновить репозитории:

```
./instead-manager.py -u
```

Поиск игры:

```
./instead-manager.py -s кот
```

Установка игры:

```
./instead-manager.py -i cat
```

Вывод списка установленных игр:

```
./instead-manager.py -ll
```

Запуск игры:

```
./instead-manager.py -r cat
```

Удаление игры:

```
./instead-manager.py -d cat
```

## GUI (instead-manager-tk.pyw)


Реализация графического интерфейса пользователя.

![alt text](https://github.com/jhekasoft/instead-manager/raw/master/docs/images/instead-manager-tk.png "instead-manager tkinter")

### Запуск:

```
python3 instead-manager-tk.pyw
```

или (с правами на исполнение)

```
./instead-manager-tk.pyw
```

В системе Windows достаточно двойного клика по файлу `instead-manager-tk.pyw`.

Если же менеджер будет у вас установлен в системе, то скорее всего его можно будет запустить стандартным образом из
списка программ вашей ОС.