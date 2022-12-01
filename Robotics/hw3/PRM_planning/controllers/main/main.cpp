#include <webots/Robot.hpp>
#include <webots/Motor.hpp>
#include <webots/Camera.hpp>
#include <webots/Gps.hpp>
#include <iostream> 
#include <algorithm>
#include <limits>
#include <string>
#include <sys/time.h>

using namespace std;
using namespace webots;

// #define TIME_STEP 64

#define SPEED1 0.8
#define SPEED2 -0.3
#define GRAY 200

int main() {
	// 初始化
    Robot *robot = new Robot();
	int timeStep = (int)robot->getBasicTimeStep();
	Camera *camera[2];
	char camera_names[2][15] = {"left_camera", "right_camera"};
    Motor *motors[4];
	char wheels_names[4][10] = {"FR_motor", "FL_motor", "BL_motor", "BR_motor"};
    GPS *gps = robot->getGPS("gps");
    gps->enable(timeStep);
	
	for (int i = 0; i < 2; i++) {
    	camera[i] = robot->getCamera(camera_names[i]);
		camera[i]->enable(timeStep);
  	}
	for (int i = 0; i < 4; i++) {
    	motors[i] = robot->getMotor(wheels_names[i]);
		motors[i]->setPosition(std::numeric_limits<double>::infinity());
		motors[i]->setVelocity(0.0);
	}
	double left_speed = SPEED1;
    double right_speed = SPEED1;

    long step = 0;
	double average_speed = 0;
	double average_position = 0;
	const double *position = nullptr;

	// 根据左右相机的灰度值控制轮子的速度
	while (robot->step(timeStep) != -1) {
		step++;
        position = gps->getValues();
		// 计算小车距离圆心的距离
        average_position += sqrt(position[0] * position[0] + position[1] * position[1]);

    	const unsigned char* left_image = camera[0]->getImage();
		const unsigned char* right_image = camera[1]->getImage();
		int height = camera[0]->getHeight();
		int width = camera[0]->getWidth();
		double count_lb = 0, count_rb = 0;
		for (int i = 0; i < width; ++i) {
			for (int j = 0; j < height; ++j) {
				// 获取左右相机每个像素点的灰度值
				int l_g = camera[0]->imageGetGray(left_image, width, i, j);
				int r_g = camera[1]->imageGetGray(right_image, width, i, j);
				count_lb += l_g;
				count_rb += r_g;
			}
		}
		// 加起来后要取平均
		count_lb /= width * height;	
		count_rb /= width * height;
 		
    	if ((count_lb <= GRAY && count_rb <= GRAY) || (count_lb > GRAY && count_rb > GRAY)) {	// 左右都低(高)往前走
      		left_speed = SPEED1;
      		right_speed = SPEED1;
    	}
    	else if (count_lb <= GRAY && count_rb > GRAY) {	// 左低右高往左偏
      		left_speed = SPEED2;
      		right_speed = SPEED1;
    	}
    	else if (count_lb > GRAY && count_rb <= GRAY) {	// 左高右低往右偏
			left_speed = SPEED1;
      		right_speed = SPEED2;
    	}
        // 计算平均速度
        average_speed = (average_speed * (step-1) + (left_speed + right_speed)/2) / step;
		// 输出距离圆心距离、平均速度、左右相机的灰度值
		printf("position: %lf, ", average_position / step);
        printf("speed: %lf,", average_speed);
		printf("left: %lf, right: %lf\n", count_lb, count_rb);

		motors[0]->setVelocity(right_speed);
     	motors[1]->setVelocity(left_speed);
     	motors[2]->setVelocity(left_speed);
     	motors[3]->setVelocity(right_speed);
  	}
    delete robot;
	return 0;
}
