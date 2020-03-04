### run app on 3000
docker run  --restart unless-stopped -it -d -p 0.0.0.0:3000:3000 -p 0.0.0.0:5000:80 --name videogen -v /home/user/flask-argon-dashboard:/workspace cloverzrg/cloud9 --auth habib:habib

### run app on 80
docker run  --restart unless-stopped -it -d -p 0.0.0.0:80:3000 -p 0.0.0.0:5000:80 --name videogen_new -v /home/user/flask-argon-dashboard:/workspace videogen_image --auth habib:habib

### authorization to site
*auth to ide*  - habib:habib

*auth to app* - admin:admin

### run redis for socketio multiprocess
sudo redis-server