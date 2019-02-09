#include <stdint.h>
#include <iostream>
#include <cstring>
#include <fstream>
#include <chrono>
#include <thread>
#include <math.h>
#include "headers/MLX90640_API.h"


#define MLX_I2C_ADDR 0x33


int main(int argc, char* argv[]){
    int state = 0;
    //printf("Starting...\n");
    static uint16_t eeMLX90640[832];
    float emissivity = 1;
    uint16_t frame[834];
    static float image[768];
    float eTa;
    static uint16_t data[768*sizeof(float)];

    float outputArray = 768;

	int FPS = 8;

	if(argc > 1){
    	FPS = strtol(argv[1], nullptr, 0);
	}

    std::cout << "capturing at: " << FPS << " FPS\n"; //print the val

    std::ofstream outfile;


    MLX90640_SetDeviceMode(MLX_I2C_ADDR, 0);
    MLX90640_SetSubPageRepeat(MLX_I2C_ADDR, 0);
    switch(FPS){
        case 1:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b001);
            break;
        case 2:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b010);
            break;
        case 4:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b011);
            break;
        case 8:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b100);
            break;
        case 16:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b101);
            break;
        case 32:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b110);
            break;
        case 64:
            MLX90640_SetRefreshRate(MLX_I2C_ADDR, 0b111);
            break;
        default:
            printf("Unsupported framerate: %d", FPS);
            return 1;
    }
    //MLX90640_SetChessMode(MLX_I2C_ADDR); //interesting...
    //MLX90640_SetSubPage(MLX_I2C_ADDR, 0);
    //printf("Configured...\n");

    paramsMLX90640 mlx90640;
    MLX90640_DumpEE(MLX_I2C_ADDR, eeMLX90640);
    MLX90640_ExtractParameters(eeMLX90640, &mlx90640);

    int refresh = MLX90640_GetRefreshRate(MLX_I2C_ADDR);
    //printf("EE Dumped...\n");

    int frames = 30;
    int subpage;
    static float mlx90640To[768];

	int fcount = 0;
	int wcount = 0;
	int loopcount = 0;

	//outfile.open ("/tmp/heatmap.csv");

    while (1){
		//outfile.clear();
		//outfile.seekp(0, std::ofstream::beg);

        state = !state;
        printf("State: %d \n", state);

		std::cout << "Trying for a frame\n";
        int t = MLX90640_GetFrameData(MLX_I2C_ADDR, frame);
		std::cout << "Frame status: ";
		std::cout << t;
		std::cout << "\n";

		printf("Frame retrieved\n");
        MLX90640_InterpolateOutliers(frame, eeMLX90640);
        eTa = MLX90640_GetTa(frame, &mlx90640);
        subpage = MLX90640_GetSubPageNumber(frame);
        MLX90640_CalculateTo(frame, &mlx90640, emissivity, eTa, mlx90640To);
        //printf("Subpage: %d\n", subpage);
        //MLX90640_SetSubPage(MLX_I2C_ADDR,!subpage);

		outfile.open ("/tmp/heatmap.csv");

		if (outfile.is_open()){
			int counter = 0;
		    for(int x = 0; x < 32; x++){
		        for(int y = 0; y < 24; y++){
		            //std::cout << image[32 * y + x] << ",";
		            float val = mlx90640To[32 * (23-y) + x];
		            if(val > 99.99) val = 99.99;
					counter++;
					//std::cout << val; //print the val
					val = roundf(val * 100) / 100;  //round to 2 dp
					//val = roundf(val); //just round
					outfile << val;
					//std::this_thread::sleep_for(std::chrono::microseconds(50)); //chill...
					//std::cout << "data write: "; //print the val
					//std::cout << wcount; //print the val
					//std::cout << "\n"; //print the val
					wcount++;
						    
					if(counter < 768) outfile << ",";//print the comma, omit the last one
				    }
		    }
		}
	outfile.close();
	//std::this_thread::sleep_for(std::chrono::milliseconds(100)); //chill...
    }
	//outfile.close();
    return 0;
}
