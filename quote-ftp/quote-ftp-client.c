#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define QUOTE_FTP_PORT 6789
#define SERVER_ADDR "128.12.85.111"

#define MAX_WINDOW_PKTS 1000
#define MAX_LENGTH_SECONDS 300

int main(int argc, char *argv[]) {
  if (argc != 4) {
    printf ("Usage: ./client <server-ip-addr> <window-in-pkts> "
            "<length-in-seconds> \n");
    return -1;
  }

  struct in_addr serv_addr;
  if (inet_aton(argv[1], &serv_addr) == 0) {
    printf ("Couldn't parse IP addr %s\n", argv[1]);
    return -1;
  }

  int window_pkts = atoi(argv[2]);
  if (window_pkts <= 0 || window_pkts > MAX_WINDOW_PKTS) {
    printf ("Invalid window argument: %s\n", argv[2]);
  }
  int n_secs = atoi(argv[3]);
  if (n_secs <= 0 || n_secs > MAX_LENGTH_SECONDS) {
    printf ("Invalid length argument: %s\n", argv[3]);
  }

  int sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1) {
    perror("socket");
    return -1;
  }

  int rcv_size = (window_pkts * 680);
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

  time_t start_time = time(NULL);
  char buf[128];
  for (;;) {
    int bytes_read = read(sock, buf, sizeof buf - 1);
    buf[bytes_read] = 0;
    time_t cur_time = time(NULL);
    if (cur_time - start_time > n_secs) {
      break;
    }
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
