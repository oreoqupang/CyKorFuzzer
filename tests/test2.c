#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>

int main(int argc, char *argv[]) {
    char buf[4];
    read(0, buf, 4);
    if(buf[0] =='f'){
        if(buf[1]=='u'){
            if(buf[2]=='z'){
                if(buf[3]!='z'){
                    printf("correct!\n");
                    return 0;
                }
            }
        }
    }
    printf("wrong");
    return -1;
}