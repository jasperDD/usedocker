#---------------------------INSTALL DOCKER IMAGE
0. cd /home/
1. sudo git clone https://github.com/jasperDD/neural_docker.git
2. cd /home/neural_docker
3. sudo docker build -t neural_cont .
4. sudo docker run --restart unless-stopped -it -d -p 0.0.0.0:80:80 --name neural_python -v /home/neural_docker:/workspace neural_cont

#---------------------------REQUESTS
1. train - curl -H "Content-Type: multipart/form-data" -F "files=@1.csv" -F "files=@2.csv" -X POST http://83.166.244.110/train
2. forecast - curl -H "Content-Type: multipart/form-data" -F "files=@1.csv" -F "files=@2.csv" -X POST http://83.166.244.110/forecast
3. forecastStr - curl -H "Content-Type: application/x-www-form-urlencoded" -d "string=OUR_STRING" -X POST http://83.166.244.110/forecastStr
