# ПУБЛИКАЦИЯ КОМИКСОВ "ВКОНТАКТЕ"

Данный скрип скачивает случайный комикс с сайта [xkcd](https://xkcd.com) и публикует его в сообществе [ВКонтакте](https://vk.com/club220987965). При каждом запуске скрипта скачивается и публикуется один случайный комикс.

## Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть есть конфликт с Python2) для установки зависимостей:

```cmd
pip install -r requirements.txt
```

## Переменные окружения

| Переменная | Где взять |
|----------|----------|
| [redirect_uri] | адрес, на который перенаправят пользователя после авторизации |
| [group_id] | id группы вк. Узнать по [ссылке](https://regvk.com/id/)  |
| [client_id] | id клиента вк. Узнать в [настройках вашего приложения](https://vk.com/apps?act=manage), раздел 'Редактировать'  |
| [upload_url] | ссылка для отправки фотографий на сервер. Получить методом [getWallUploadServer](https://vk.com/dev/photos.getWallUploadServer) |
| [access_token] | личный токен доступа, необходимый для подключения к api сайта [vk.com.](https://vk.com/) Для получения секретного токена рекомендуется использовать процедуру [Implicit Flow](https://vk.com/dev/implicit_flow_user) |

## Параметры

При запуске скрипта, можно указать параметр [--path] который изменит имя папки, в которую скачивается комикс. По умолчанию, она называется 'comics'.

### Пример

```cmd
python main.py --image
```

Также скрипт запускается без параметра.
