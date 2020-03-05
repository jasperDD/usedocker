### Среда 
linux vps (ubuntu) с установленным docker

### Копирование репозитория github.com с приложением 

### Копирование докер контейнера с репозитория hub.docker.com



### Запуск контейнера на VPS с приложением на 80 м порте и редактором на 5199 порте

docker run  --restart unless-stopped -it -d -p 0.0.0.0:80:3000 -p 0.0.0.0:5000:80 --name videogen_new -v /home/user/flask-argon-dashboard:/workspace videogen_image --auth habib:habib

### Данные авторизации в редакторе
habib:habib
### Данные авторизации на сайте по умолчанию
admin:admin

### Запуск redis сервера приложения внутри редактора
sudo redis-server

### Запуск самого приложения внутри редактора
