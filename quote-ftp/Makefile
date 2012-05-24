CC := gcc
CFLAGS := -g -Wall

default: all


.PHONY: all
all: client server

client: quote-ftp-client.o
	$(CC) $(CFLAGS) -o $@ $<

server: quote-ftp-server.o
	$(CC) $(CFLAGS) -o $@ $<

.PHONY: clean
clean:
	@rm -r client server *.o
