CC      = gcc
CFLAGS  = -Wall -O0 -fno-stack-protector -no-pie -static
TARGET  = biosynthd

all: $(TARGET)

$(TARGET): service.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)
