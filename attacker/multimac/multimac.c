/*
 *  MultiMAC
 *
 *  Copyright (c) 2005-2008 Primiano Tucci
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <stdlib.h>
#include <stddef.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <linux/if.h>
#include <linux/if_tun.h>
#include <net/ethernet.h>
#include <errno.h>
#include "pthread.h"

#define RSIZE 1550
#define HUBMODE

static int *tap;
static int Ntap;

int tun_alloc(char *dev)
{

   struct ifreq ifr;
   int fd, err;

   if( (fd = open("/dev/net/tun", O_RDWR)) < 0 )
     perror("open()");

   memset(&ifr, 0, sizeof(ifr));

         /* Flags: IFF_TUN   - TUN device (no Ethernet headers)
	  *        *        IFF_TAP   - TAP device
	  *        *
	  *        *        IFF_NO_PI - Do not provide packet information
	  *        */
   ifr.ifr_flags = IFF_TAP;
   if( *dev )
     strncpy(ifr.ifr_name, dev, IFNAMSIZ);

   if( (err = ioctl(fd, TUNSETIFF, (void *) &ifr)) < 0 )
     {

	close(fd);
	return err;
     }

   strcpy(dev, ifr.ifr_name);
   return fd;
}

void PrintUsage(){
   printf("Usage: multimac <number of taps>\n\n");
   exit(-1);
}

static void * TMasterThread(void *arg)
{

  char buf[RSIZE];
  int i,recSize;
   
  while(1)
     {   
	recSize=read(tap[0],buf,sizeof(buf));
	for(i=1;i<Ntap;i++)
	  write(tap[i],buf,recSize);
     }
}

static void * TIfaceThread(void *arg)
{
   char buf[RSIZE];
   int recSize;
   int *curtap=(int *)arg;
   while(1)
     {
	recSize=read(tap[*curtap],buf,sizeof(buf));
	write(tap[0],buf,recSize);
	  }
}

void DaemonBanner()
{

  printf("\n.:: Gone into daemonland ::.\n");
/*  int a,i; 
   printf("\n.:: Stairway to daemonland ::.\n");
   printf("_");
   for(i=0;i<6;i++)
     {
	for(a=0;a<i;a++)
	  printf("==");
	printf("=|_\n");
	usleep(100000);
     }
   printf("\n.:: Welcome into daemonland ::.\n");
*/
}

int main(int argc, char *argv[])
{
   int i;
   int *ipoint;
   char strTap[6];
   pthread_t *threads;
   
   if(argc<2)
     PrintUsage();
   if((Ntap=atoi(argv[1]))<1)
     PrintUsage();
   
   printf("Allocating %d taps... \n",Ntap);
   Ntap++;
   tap=(int *)calloc(Ntap,sizeof(int));
   threads=(pthread_t *)calloc(Ntap,sizeof(pthread_t));
  
   for(i=0;i<Ntap;i++)
     {
	printf("\r%d of %d",i,Ntap-1);
	fflush(stdout);
        sprintf(strTap,"tap%d",i);
	if((tap[i]=tun_alloc(strTap))<=0)
	  {
	     perror("ioctl()");
	     exit(1);

	  }
	
     }

   DaemonBanner();
   
   if(fork())
     exit(0);
   setsid();
   usleep(500);
   printf("Starting Master Thread... ");
   if(pthread_create(&(threads[0]),NULL,TMasterThread,(void *) NULL))
     {   
	perror("pthread_create()");
	exit(1);
     }
   
   printf("OK\n");
   
   pthread_attr_t thread_attr;


    if (pthread_attr_init(&thread_attr) != 0) {
       printf("failed init\n");
        exit(1);
   }

    if (pthread_attr_setstacksize(&thread_attr, 512*1024)!= 0) {
       printf("failed stack size\n");
        exit(1);
    }
  
   printf("Starting Interface Threads... \n");
   for(i=1;i<Ntap;i++)
     {
	printf("\r%d of %d",i,Ntap-1);
	fflush(stdout);
	ipoint=(int *)calloc(1,sizeof(int));
	*ipoint=i;
	if(pthread_create(&(threads[i]),&thread_attr,TIfaceThread,(void*)ipoint))
	  {
	     perror("pthread_create()");
	     exit(-1);
	  }
	
     }
   pause();

   return 0;
}

