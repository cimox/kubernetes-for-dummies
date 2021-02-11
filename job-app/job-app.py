import os

JOB_TYPE = os.getenv('JOB_TYPE', 'stateless')
EDGE_API_URL = os.getenv('EDGE_API_URL', 'http://cluster-dns.edge.edge-app')
DISK_PATH = os.getenv('DISK_PATH', '/mnt/storage')
FIB_N = int(os.getenv('FIB_N', 35))


def do_the_job(job_type):
    print(f'Working hard on {job_type}')

    if job_type == 'stateless':
        n = fib(FIB_N)

        print(f'Before disk write: {os.listdir(DISK_PATH)}')

        with open(os.path.join(DISK_PATH, str(FIB_N) + '.txt'), 'w') as f:
            f.write(str(n))

        print(f'After disk write: {os.listdir(DISK_PATH)}')

        return n
    elif job_type == 'stateful':
        n = None
        files = os.listdir(DISK_PATH)
        print(f'Before disk write: {files}')

        if str(FIB_N) + '.txt' in set(files):  # Try to load pre-calculated fib number from disk
            path = os.path.join(DISK_PATH, str(FIB_N) + '.txt')
            print(f'Reading pre-calculated fib number from file {path}')
            with open(path, 'r') as f:
                n = f.readline()

        if n is None:
            n = fib(FIB_N)
            with open(os.path.join(DISK_PATH, str(FIB_N) + '.txt'), 'w') as f:
                f.write(str(n))

            print(f'After disk write: {os.listdir(DISK_PATH)}')

        return int(n)

    print('Nothing to return...')


def fib(n):
    if n <= 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)


if __name__ == "__main__":
    do_the_job(JOB_TYPE)
