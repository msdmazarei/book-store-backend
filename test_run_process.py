import subprocess


def main():
    DETACHED_PROCESS = 0x00000008
    results = subprocess.Popen(
        ['/home/nsm/PycharmProjects/online_library/sample_runnable_code.py'],
        close_fds=True, stdout=subprocess.PIPE)
    streamdata = results.communicate()[0]

    print(results.returncode)
    print(streamdata)

    return streamdata


if __name__ == '__main__':
    main()
