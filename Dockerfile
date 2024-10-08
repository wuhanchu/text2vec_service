FROM wuhanchu/centos:torch


# RUN groupadd -r mygroup && useradd --no-log-init -r -g mygroup myuser
# USER myuser

WORKDIR /opt/service/
COPY "./" "./"

RUN chmod +x ./run.sh 
RUN pip3 install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ./run.sh