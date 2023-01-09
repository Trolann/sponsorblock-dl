FROM trolann/rbimage:latest

RUN mkdir -p /sponsorblock-dl
RUN pip3 install pillow
RUN pip3 install moviepy
RUN pip3 install sponsorblock
RUN pip3 install pytube

COPY . '/sponsorblock-dl'

CMD ["sponsorblock-dl/main.py"]