FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    aria2 adb git libgl1 libglib2.0-0 python3-pip && \
    pip install uv

RUN git clone https://github.com/BlueArchiveArisHelper/BAAH.git --depth=1

RUN python3 BAAH/requireforyou.py --core && \
    uv pip install -r /app/BAAH/requireforyou.txt --system

RUN cp /app/BAAH/docker.sh /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]