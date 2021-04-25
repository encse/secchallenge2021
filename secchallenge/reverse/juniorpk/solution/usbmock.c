#define _GNU_SOURCE


#include <stdio.h>
#include <string.h>
#include <libusb-1.0/libusb.h>
#include <dlfcn.h>


void hexdump(const void* data, size_t size) {
	char ascii[17];
	size_t i, j;
	ascii[16] = '\0';
	for (i = 0; i < size; ++i) {
		printf("%02X ", ((unsigned char*)data)[i]);
		if (((unsigned char*)data)[i] >= ' ' && ((unsigned char*)data)[i] <= '~') {
			ascii[i % 16] = ((unsigned char*)data)[i];
		} else {
			ascii[i % 16] = '.';
		}
		if ((i+1) % 8 == 0 || i+1 == size) {
			printf(" ");
			if ((i+1) % 16 == 0) {
				printf("|  %s \n", ascii);
			} else if (i+1 == size) {
				ascii[(i+1) % 16] = '\0';
				if ((i+1) % 16 <= 8) {
					printf(" ");
				}
				for (j = (i+1) % 16; j < 16; ++j) {
					printf("   ");
				}
				printf("|  %s \n", ascii);
			}
		}
	}
}


int LIBUSB_CALL libusb_get_device_descriptor(
    libusb_device *dev,
	struct libusb_device_descriptor *desc)
{

    int (*original)(libusb_device *dev, struct libusb_device_descriptor *desc);

    original = dlsym(RTLD_NEXT, "libusb_get_device_descriptor");
    int res = (*original)(dev, desc);

    // 0x002180ee
    uint8_t* raw = ((uint8_t*)desc);
    if (raw[8] == 0xee && raw[9] == 0x80) {
        raw[8] = 0x37;
        raw[9] = 0x13;
        raw[10] = 0x37;
        raw[11] = 0x13;

    }
    
    // hexdump(desc, 0x100);
    // desc->idVendor = 0x1337;
    // desc->idProduct = 0x0000;

    printf("%04x:%04x (bus %d, device %d)\n",
        desc->idVendor, desc->idProduct,
        libusb_get_bus_number(dev), libusb_get_device_address(dev));
    
    printf("desc location: %p\n", (char *)(void*)desc);

    // libusb_device_handle *devh = NULL;
    // libusb_init(NULL);
    

    // int returnValue = libusb_open( dev, &devh );

    // if (devh != NULL) {
    //     uint8_t data[42];
    //     uint16_t lang;

    //     if(desc->iManufacturer) {
    //         libusb_get_string_descriptor_ascii( devh, desc->iManufacturer, data, 42 );
    //         printf("  %s\n", data);
    //     }
    //     if(desc->iProduct) {
    //         libusb_get_string_descriptor_ascii( devh, desc->iProduct, data, 42 );
    //         printf("  %s\n", data);
    //     }

    //     printf("idVendor location: %p\n", (char *)(void*)desc);

        
    // } else {
    //     printf("coki\n");
    // }

    // if (devh != NULL)
    //     libusb_close( devh );

    puts("press enter");
    // char buff[10];
    // fgets (buff, 10, stdin);

    return res;
}