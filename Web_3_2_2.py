from multiprocessing import Pool, current_process,cpu_count
import logging
from datetime import datetime

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def factorize(params):
    name = current_process().name
    result = []
    t_start = datetime.now()
    i = 1
    while i <= params:
        if params % i == 0:
            result.append(i)
        i += 1
    logger.debug(f'Done: {name} -- {datetime.now() - t_start} -- {result}')
    return result


if __name__ == '__main__':
    c = cpu_count()
    with Pool(processes=c) as pool:
        a, b, c, d = pool.map(factorize, (128, 255, 99999, 10651060))
        logger.debug(a)
        logger.debug(b)
        logger.debug(c)
        logger.debug(d)