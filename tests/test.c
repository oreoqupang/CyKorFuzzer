#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s [Signal]\n", argv[0]);
        fprintf(stderr, "\tEx) %s %d -> kill with SIGKILL\n", argv[0], SIGKILL);
        exit(-1);
    }
    kill(getpid(), atoi(argv[1]));
    return 0;
}