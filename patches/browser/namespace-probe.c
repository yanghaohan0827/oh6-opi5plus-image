#define _GNU_SOURCE
#include <sched.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
int main(void){long p=syscall(SYS_clone,CLONE_NEWPID|CLONE_NEWNET|SIGCHLD,0,0,0,0);if(p<0){printf("namespace clone failed: errno=%d %s\n",errno,strerror(errno));return 1;}if(p==0){printf("render-style namespace child pid=%d\n",(int)syscall(SYS_getpid));fflush(stdout);_exit((int)syscall(SYS_getpid)==1?0:2);}int s=0;waitpid(p,&s,0);printf("namespace clone succeeded, child status=%d\n",s);return s;}
