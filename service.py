from flask import Flask, request, Response
import jaydebeapi
import json
from sesamutils.flask import serve
from sesamutils import VariablesConfig, sesam_logger
import sys

app = Flask(__name__)
logger = sesam_logger('DB2(AS400)-Service')

required_env_vars = ["username", "password", "host", "dbname", "batch_size"]
optional_env_vars = [("LOG_LEVEL", "INFO")]

config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)

db = config.dbname
logger.info(f'com.ibm.as400.access.AS400JDBCDriver, jdbc:as400://{config.host}/M3FDBTST,[{config.username}, config.password], ./jt400.jar')


def get_jdbc_connection():
    try:
        import jpype
        if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
            jpype.java.lang.Thread.currentThread().setContextClassLoader(jpype.java.lang.ClassLoader.getSystemClassLoader())
        connection = jaydebeapi.connect(
            'com.ibm.as400.access.AS400JDBCDriver',
            f'jdbc:as400://{config.host}:{config.dbname}', 
            [config.username ,config.password], 
            './jt400.jar', ''
        )
        return connection
    except Exception as e:
        logger.error("Exception\n" + str(e))

def stream_as_json(generator_function):
    first = True
    yield '['
    for item in generator_function:
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(item)
    yield ']'

def connection(id, lm, dbtable, since):
    try:
        conn = get_jdbc_connection()
        count = 0
        curs = conn.cursor()
        curs.execute(f'SELECT CAST({id} AS VARCHAR(20)) AS \"_id\", {lm} AS \"_updated\", {dbtable}.* FROM {dbtable} WHERE {lm} > {since} ORDER BY {lm}')
        logger.info('Query sent: ')
        logger.info(f'SELECT CAST({id} AS VARCHAR(20)) AS \"_id\", {lm} AS \"_updated\", {dbtable}.* FROM {dbtable} WHERE {lm} > {since} ORDER BY {lm}')
        
        # rowcount = curs.rowcount()
        # logger.info(".rowcount = "+ str(rowcount))

        header = [i[0] for i in curs.description]
        # dataset = curs.fetchall()
        dataset = curs.fetchmany(size=int(config.batch_size))
        logger.info('Columns fetched! Starting entity stream...')
        while len(dataset) > 0:
            yieldcount = 0
            for row in dataset:
                yield dict(zip(header, row))
                count += 1
                yieldcount += 1 
            logger.info(f'Yielded {yieldcount} rows')
            dataset = curs.fetchmany(size=int(config.batch_size))
        logger.info(f'Returned {str(count)} rows')
        try:
            curs.close()
            conn.close()
            logger.info(f"Connection to db {dbtable} closed. ")
        except Exception as e:
            logger.info("Could not close connection due to error: " + str(e))

        # logger.info(json.dumps(dict(zip(header, row))))
        # logger.info(json.dumps(row[0]).strip())
        # logger.info([row.strip() if isinstance(row,str) else row])
        # logger.info(type(row[0]))
        # logger.info(json.dumps(dict(zip(header, [row.strip() if isinstance(row,str) else row]))))

    except Exception as e:
        logger.error("Error: " + str(e))

@app.route("/", methods=['GET'])
def get():
    # body = request.json
    lm = request.args.get('lm')
    id = request.args.get('id')
    table = request.args.get('table')
    since = request.args.get('since')
    dbtable = f"{db}.{table}"

    try: 
        return Response(stream_as_json(connection(id,lm,dbtable, since)), mimetype='application/json')
    except Exception as e:
        logger.error("Exception\n" + str(e))

if __name__ == '__main__':
    
    with open("banner.txt", 'r', encoding='utf-8') as banner:
        logger.info('Initialisation...  v.0.02\n\n' + banner.read() + '\n')
    try:
        logger.info("LOG_LEVEL = %s" % logger.level)
    except: 
        logger.error("Could not print log level")

    logger.info("Starting Cherrypy...")
    serve(app)