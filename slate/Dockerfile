FROM ruby:2.5

RUN apt update && apt -y install nodejs
RUN gem install bundler

ADD . /slate
WORKDIR /slate

RUN bundle update --bundler
RUN bundler install

CMD ["./deploy.sh", "--source-only"]

