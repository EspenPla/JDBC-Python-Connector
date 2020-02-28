# JDBC-Python-Connector
Using JPype1 and jaydebeapi with JDBC to make queries and streaming the results. 

The connector is currently using the JDBC for AS400. 

# SESAM SYSTEM CONFIG #

{
  "_id": "<system-name>",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "INFO",
      "batch_size": <batch_size>,
      "dbname": "<dbname>",
      "host": "<host>",
      "password": "$SECRET(password)",
      "username": "<username>"
    },
    "image": "espenplatou/jdbc:test",
    "port": 5000
  }
}

# SESAM PIPE CONFIG #
{
  "_id": "<PIPE-ID>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<SYSTEM-ID>",
    "url": "/?id=<TABLE-ID>&lm=<LAST-MODIFIED-FIELD>&table=<TABLE-NAME>&since=<OPTIONAL(SINCE-VALUE)"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}
