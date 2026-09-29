#include "write.h"
#include <stdlib.h>
#include <stdio.h>

#pragma pack(push, 1)
typedef struct {
    uint16_t bfType;
    uint32_t bfSize;
    uint16_t bfReserved1;
    uint16_t bfReserved2;
    uint32_t bfOffBits;
} BITMAPFILEHEADER;

typedef struct {
    uint32_t biSize;
    int32_t biWidth;
    int32_t biHeight;
    uint16_t biPlanes;
    uint16_t biBitCount;
    uint32_t biCompression;
    uint32_t biSizeImage;
    int32_t biXPelsPerMeter;
    int32_t biYPelsPerMeter;
    uint32_t biClrUsed;
    uint32_t biClrImportant;
} BITMAPINFOHEADER;
#pragma pack(pop)

int write_RGBA_to_png(uint16_t width, uint16_t height, uint8_t * array, const char * filename)
{
    // Write as BMP instead since we drop libpng dependency for Windows ease
    FILE * fp = fopen(filename, "wb");
    if(fp == NULL) return 0;
    
    BITMAPFILEHEADER bfh;
    BITMAPINFOHEADER bih;
    
    bfh.bfType = 0x4D42; // 'BM'
    bfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfh.bfSize = bfh.bfOffBits + (width * height * 4);
    bfh.bfReserved1 = 0;
    bfh.bfReserved2 = 0;
    
    bih.biSize = sizeof(BITMAPINFOHEADER);
    bih.biWidth = width;
    bih.biHeight = -height; // Top-down
    bih.biPlanes = 1;
    bih.biBitCount = 32;
    bih.biCompression = 0; // BI_RGB
    bih.biSizeImage = width * height * 4;
    bih.biXPelsPerMeter = 0;
    bih.biYPelsPerMeter = 0;
    bih.biClrUsed = 0;
    bih.biClrImportant = 0;
    
    fwrite(&bfh, sizeof(BITMAPFILEHEADER), 1, fp);
    fwrite(&bih, sizeof(BITMAPINFOHEADER), 1, fp);
    
    // BGRA format for BMP
    for(int y = 0; y < height; y++) {
        for(int x = 0; x < width; x++) {
            int idx = (y * width + x) * 4;
            uint8_t rgba[4];
            rgba[0] = array[idx + 2]; // B
            rgba[1] = array[idx + 1]; // G
            rgba[2] = array[idx + 0]; // R
            rgba[3] = array[idx + 3]; // A
            fwrite(rgba, 4, 1, fp);
        }
    }
    
    fclose(fp);
    return 1;
}
