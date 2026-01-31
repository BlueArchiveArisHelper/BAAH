FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 adb libglib2.0-0 git && apt-get clean

RUN git clone https://github.com/sanmusen214/BAAH -b dev --depth=1

COPY requirements.txt .

RUN sed -i '/^altgraph==0.17.4/d; \
            /^argcomplete==3.1.1/d; \
            /^bottle==0.12.25/d; \
            /^cffi==1.16.0/d; \
            /^clr-loader==0.2.6/d; \
            /^colorama==0.4.6/d; \
            /^exceptiongroup==1.2.0/d; \
            /^pefile==2023.2.7/d; \
            /^pipx==1.2.0/d; \
            /^proxy_tools==0.1.0/d; \
            /^pycparser==2.21/d; \
            /^pyinstaller==6.2.0/d; \
            /^pyinstaller-hooks-contrib==2023.10/d; \
            /^pyreadline3==3.4.1/d; \
            /^pythonnet==3.0.3/d; \
            /^pywebview==4.4.1/d; \
            /^pywin32-ctypes==0.2.2/d; \
            /^userpath==1.9.1/d' requirements.txt

RUN pip --default-timeout=100 --no-cache-dir --disable-pip-version-check --retries=50 install -r requirements.txt

RUN mkdir -p ~/.ssh && echo -e "Host *\n    StrictHostKeyChecking accept-new" >> ~/.ssh/config

RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'cd /app/BAAH' >> /app/start.sh && \
    echo 'git pull' >> /app/start.sh && \
    echo 'python jsoneditor.py --no-show' >> /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
