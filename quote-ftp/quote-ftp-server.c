#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#define QUOTE_FTP_PORT 6789

static char send_buf[1001];
static void fill_ftps();

int main(int argc, char *argv[]) {
  struct timeval tv[1];
  gettimeofday(tv, NULL);
  srand(tv->tv_usec);
  fill_ftps();
  send_buf[999] = '\n';
  int sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1) {
    perror("socket");
    return -1;
  }
  
  int reuse = 1;
  if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof reuse)
      == -1) {
    perror ("setsockopt");
    return -1;
  }

  struct sockaddr_in sa[1];
  sa->sin_family = AF_INET;
  sa->sin_port = htons(QUOTE_FTP_PORT);
  sa->sin_addr.s_addr = INADDR_ANY;
  memset(&sa->sin_zero, 0, sizeof sa->sin_zero);

  if (bind(sock, (struct sockaddr*)sa, sizeof *sa) == -1) {
    perror ("bind");
    return -1;
  }

  if (listen(sock, 1) == -1) {
    perror ("listen");
    return -1;
  }
  printf ("Waiting for connections on port %d\n", QUOTE_FTP_PORT);

  struct sockaddr_in client_sa[1];
  socklen_t client_sa_len = sizeof *client_sa;

  int conn = accept(sock, (struct sockaddr*)client_sa, &client_sa_len);
  if (conn == -1) {
    perror("accept");
    return -1;
  }
  printf ("Got a connection, sending data\n");

  const char *to_send = send_buf;
  int send_len = strlen(send_buf);
  for (;;) {
    int ret = send(conn, to_send, send_len, MSG_NOSIGNAL);
    if (ret < 0) {
      printf ("Write failed, breaking out\n");
      break;
    }
    // Sleep uniform [0, 0.17ms]
    int sleep_time = rand() % 170;
    usleep(sleep_time);
  }

  close(conn);
  printf ("Send done, exiting\n");
  close (sock);
  return 0;
}

static void fill_ftps() {
  int num_ftps = sizeof send_buf / 3;
  const char *ftp = "ftp";
  int i, p = 0;
  for (i = 0; i < num_ftps; ++i, p += 3) {
    memcpy(send_buf + p, ftp, 3);
  }
}
