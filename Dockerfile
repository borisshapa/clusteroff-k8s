FROM apache/spark:3.4.1-scala2.12-java11-python3-ubuntu

WORKDIR /app

USER root

ENV PYSPARK_SUBMIT_ARGS="--packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 --conf spark.cassandra.connection.host=cassandra pyspark-shell"

COPY requirements.txt /app

RUN ln -sf $(which python3) /usr/bin/python && \
    ln -sf $(which pip3) /usr/bin/pip

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

#ENTRYPOINT ["bash"]