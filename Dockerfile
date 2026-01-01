FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 adb aria2 libglib2.0-0 git python3-pip && apt-get clean

# RUN git clone https://github.com/BlueArchiveArisHelper/BAAH.git --depth=1
RUN git clone https://github.com/BlockHaity/BAAH.git -b Feat-crossplatfrom --depth=1

COPY requirements.txt .

RUN pip install uv

RUN python3 BAAH/requirforyou.py --core && cp BAAH/requirforyou.txt .

RUN uv pip install -r requirforyou.txt --system

RUN mkdir -p ~/.ssh && echo -e "Host *\n    StrictHostKeyChecking accept-new" >> ~/.ssh/config

RUN cp /app/BAAH/docker_start.sh /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]