from multiprocessing import Process, Manager, current_process, cpu_count
import logging
from datetime import datetime

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def example_work(params, val: Manager):
    name = current_process().name
    #logger.debug(f'Started: {name}')
    t_start = datetime.now()
    result = []
    i = 1
    while i <= params:
        if params % i == 0:
            result.append(i)
        i += 1
    #val.append(result)
    val[name] = result
    logger.debug(f'Done: {name} -- {datetime.now() - t_start} -- {result}')


def factorize(*number):
    logger.debug('With using processes')
    with Manager() as manager:
        cc = cpu_count()
        m = manager.dict()
        #m = manager.list()
        processes = []
        result = []

        for d in number:
            pr = Process(target=example_work, args=(d,m))
            pr.start()
            processes.append(pr)

        [el.join() for el in processes]
        logger.debug('End program')
        list_result = []
        for _, v in m.items():
            list_result.append(v)

        return list_result


def factorize_line(*number) -> list:
    logger.debug('Without using processes')
    t_start = datetime.now()
    result_oll = []
    for d in number:
        result = []
        i = 1
        while i <= d:
            if d % i == 0:
                result.append(i)
            i += 1
        logger.debug(f' {datetime.now()-t_start} --{result} ')
        result_oll.append(result)
    logger.debug(result_oll)
    return result_oll


if __name__ == '__main__':
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    a1, b1, c1, d1 = factorize_line(128, 255, 99999, 10651060)


