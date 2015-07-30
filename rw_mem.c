#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <errno.h>

#define PAGE_SIZE (getpagesize())
#define MAP_MASK (PAGE_SIZE - 1)

#define MODE_READ 1
#define MODE_WRITE 2

#define VPRINT(...) if (verbose) {printf(__VA_ARGS__); fflush(stdout);}

#define FATAL do { fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
			   __LINE__, __FILE__, errno, strerror(errno)); exit(1); } while(0)

int verbose = 0;

void usage(int argc, char **argv)
{
  printf("%s: -r|-w [-v] -a address [-f filename] [-s size] [-c char|-h hex]\n", argv[0]);
  printf("\t-r: read (default)\n\t-w: write\n");
  printf("\t-v: verbose\n");
  printf("\t-a address: address to start writing to or reading from\n");
  printf("\t-f filename: file to write to the memory\n");
  printf("\t-s size: number of byte to read or write\n");
  printf("\t-c char: character to write to memory (as in memset)\n");
  printf("\t-h hex: byte value to write to memory (as in memset)\n");
}

void do_read(void *vaddr, off_t size, off_t address) {
  VPRINT("do read: vaddr: %p, size: %u\n", vaddr, size);
  int bytes_read = 0;
  while (bytes_read < size) {
    if (bytes_read % 16 == 0) {
      printf("0x%08x: ", address + bytes_read);
    }
    printf("0x%02x ", ((char*)vaddr)[bytes_read]);
    bytes_read++;
    if (bytes_read % 16 == 0 && bytes_read < size) {
      printf("\n");
    }
  }
  printf("\n");
}

void do_write(void *vaddr, off_t size, char value, int file_fd) {
  VPRINT("do write: vaddr: %p, size: %u, value: %x, file_fd: %d\n", vaddr, size, value, file_fd);
  if (file_fd >= 0) {
    if (read(file_fd, vaddr, size) < size) FATAL;
    close(file_fd);
    VPRINT("Wrote %u bytes from file to %p\n", size, vaddr);
  } else {
    memset(vaddr, value, size);
    VPRINT("memset %u bytes of %c to %p\n", size, value, vaddr);
  }
}

int main(int argc, char **argv)
{
  char ch;
  char *filename = NULL;
  off_t address = 0;
  off_t map_size = 0, size = 0;
  char value = 0;
  int map_fd, file_fd = -1;
  void *map_base, *vaddr;
  int mode = MODE_READ;

  if (argc <= 1) {
    usage(argc, argv);
    exit(0);
  }
  int done = 0;
  while ((ch = getopt(argc, argv, "rwva:f:s:c:h:")) != -1) {
    switch (ch) {
    case 'r':
      mode = MODE_READ;
      break;
    case 'w':
      mode = MODE_WRITE;
      break;
    case 'v':
      verbose = 1;
      break;
    case 'a':
      address = strtoul(optarg, 0, 0);
      break;
    case 'f':
      filename = optarg;
      break;
    case 's':
      size = strtoul(optarg, 0, 0);
      break;
    case 'c':
      value = (char)optarg[0];
      break;
    case 'h':
      value = (char)strtoul(optarg, 0, 0);
      break;
    case '?':
    default:
      //printf("got unknown arg: %c (%d, %x)\n", ch, ch, ch);
      //usage(argc, argv);
      // on the odroid we get extra garbage after the arguments, so jump out without error.
      done = 1;
    }
    if (done) break;
  }

  if ((map_fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;
  VPRINT("/dev/mem opened.\n");

  if (filename != NULL) {
    struct stat stat_buf;
    if ((file_fd = open(filename, O_RDONLY)) == -1) FATAL;
    if (fstat(file_fd, &stat_buf) == -1) FATAL;
    size = stat_buf.st_size;
    VPRINT("File: %s opened, size: %u.\n", filename, size);
  }

  map_size = size + PAGE_SIZE;
  map_base = mmap(0, map_size, PROT_READ | PROT_WRITE, MAP_SHARED, map_fd, address & ~MAP_MASK);
  if(map_base == (void *) -1) FATAL;
  vaddr = (void*) ((int) map_base + (address & MAP_MASK));
  VPRINT("Memory mapped at address %p using offset %p.\n", map_base, (void*)address);

  if (mode == MODE_READ) {
    do_read(vaddr, size, address);
  } else if (mode = MODE_WRITE) {
    do_write(vaddr, size, value, file_fd);
  }

  VPRINT("Done.\n");
  if (munmap(map_base, map_size) == -1) FATAL;
  close(map_fd);
  return 0;
}
