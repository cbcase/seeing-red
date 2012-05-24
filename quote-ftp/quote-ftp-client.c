#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/types.h>
#include <sys/socket.h>

#define QUOTE_FTP_PORT 6789
#define SERVER_ADDR "128.12.85.111"

int main(int argc, char *argv[]) {
  if (argc != 2) {
    printf ("Usage: ./client <server-ip-addr>\n");
    return -1;
  }

  struct in_addr serv_addr;
  if (inet_aton(argv[1], &serv_addr) == 0) {
    printf ("Couldn't parse IP addr %s\n", argv[1]);
    return -1;
  }

  int sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1) {
    perror("socket");
    return -1;
  }

  int rcv_size = 5500;
  if (setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &rcv_size,
                 sizeof rcv_size) == -1) {
    perror ("setsockopt");
    return -1;
  }

  struct sockaddr_in sa[1];
  sa->sin_family = AF_INET;
  sa->sin_port = htons(QUOTE_FTP_PORT);
  sa->sin_addr = serv_addr;
  memset(&sa->sin_zero, 0, sizeof sa->sin_zero);

  printf ("Connecting to %s port %d\n", inet_ntoa(sa->sin_addr),
          ntohs(sa->sin_port));

  if (connect(sock, (struct sockaddr*)sa, sizeof *sa) == -1) {
    perror("connect");
    return -1;
  }

  char buf[128];
  for (;;) {
    int bytes_read = read(sock, buf, sizeof buf - 1);
    buf[bytes_read] = 0;
    printf ("I read %d bytes\n", bytes_read);
  }
  close (sock);
  return 0;
}

// IF WE WANT TO CONNECT TO A HOSTNAME RATHER THAN IP ADDR, NEED THE
// FOLLOWING CODE TO GET IP ADDR:
  /*
  struct addrinfo ai_restrictions[1];
  memset(ai_restrictions, 0, sizeof *ai_restrictions);
  ai_restrictions->ai_family = AF_INET;
  ai_restrictions->ai_socktype = SOCK_STREAM;

  struct addrinfo *ai_result;
  int res;
  if ((res = getaddrinfo(SERVER_NAME, NULL, ai_restrictions, &ai_result))
      != 0) {
    printf("getaddrinfo: %s\n", gai_strerror(res));
  }
  struct sockaddr_in *serv_addr = (struct sockaddr_in*)ai_result->ai_addr;
  */
