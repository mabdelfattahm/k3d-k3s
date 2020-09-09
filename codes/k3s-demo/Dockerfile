FROM adoptopenjdk/openjdk11:alpine-jre

ENV APPLICATION_USER ktor
RUN adduser -D -g '' $APPLICATION_USER

RUN mkdir /app
RUN chown -R $APPLICATION_USER /app

USER $APPLICATION_USER

COPY ./build/libs/k3s-demo.jar /app/k3s-demo.jar
WORKDIR /app

CMD ["java", "-server", "-XX:+UseContainerSupport", "-jar", "k3s-demo.jar"]