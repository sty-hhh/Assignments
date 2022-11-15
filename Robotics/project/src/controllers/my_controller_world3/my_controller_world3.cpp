#include <webots/Camera.hpp>
#include <webots/DistanceSensor.hpp>
#include <webots/InertialUnit.hpp>
#include <webots/Lidar.hpp>
#include <webots/Motor.hpp>
#include <webots/Robot.hpp>
#include <webots/utils/AnsiCodes.hpp>
#include <webots/GPS.hpp>
#include <webots/Node.hpp>
#include <webots/Display.hpp>

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <fstream>
#include <limits>
#include <cmath>
#include <string>

#define Pi 3.1415
#define node_quantaty 50000     //RRT随机点数量
#define path_length 0.5         //路径一段0.5m
#define path_zone 0.6           //每条路径检测周围的障碍点的范围
#define target_map_x -4.5       //终点x
#define target_map_y -4.5       //终点y
#define width 10.0              //地图宽
#define height 10.0             //地图高
#define map_rate 10.0           //建模比例

using namespace std;
using namespace webots;

/*地图点*/
struct point {
    double x;
    double y;
    bool Is_pass;
};

/*路径点*/
struct node {
    double x;
    double y;
    int last_node;
};

/*map class*/
class map {
public:
    point p[int(width*map_rate)][int(height*map_rate)];
    map() {
        for (int i = 0; i < width*map_rate; i++)
            for(int j = 0; j < height*map_rate; j++) {
                p[i][j].x =  i/map_rate - width/2;
                p[i][j].y = -j/map_rate + height/2;   //绝对位置
                p[i][j].Is_pass = true; //false代表墙
            }
    }
    void set_point(point &e, int V) {
        e.Is_pass = V;
    }
    //激光雷达坐标转换：用于统一地图坐标和小车坐标
    point turn_coordinate(double x_car, double y_car, double angle_car, double x_lidar, double y_lidar) {
        point p;
        double angle = angle_car;   // imu的roll角度
        p.x = x_car + y_lidar * cos(angle) - x_lidar * sin(angle);
        p.y = y_car + y_lidar * sin(angle) + x_lidar * cos(angle);
        p.x = round(p.x*map_rate)/map_rate;
        p.y = round(p.y*map_rate)/map_rate;
        p.Is_pass = false;
        return p;
    }
};

/*robot class*/
class Mazerobot : public Robot {
public:     //函数
    Mazerobot();
    void control();
    int  point2point(double imu, double x_car, double y_car, double x_target, double y_target);
    void go(double speed1, double speed2, double speed3, double speed4, double p1, double p2);
    void get_rrtroad(map &m,double x_car,double y_car);

public:     //一些过程变量
    int t = 0;
    int reverse_order_save = 1;     //保存路径总节点数
    int step_first = 1;             //几步检查一次路径
    node rand_path[node_quantaty];  //采样路径的节点
    node final_path[node_quantaty]; //rrt路径的节点
    node rand_n[node_quantaty];     //采样点的节点

private:
    enum Mode {GET_PATH, GO, FINISH, STOP};
    int timeStep;
    Mode mode;
    Display *display;
    GPS *Gps;
    Lidar *lid;
    Motor *motors[6];
    InertialUnit *imu;
};

/*define device and init*/
Mazerobot::Mazerobot() {
    timeStep = 32; 
    lid = getLidar("lidar");
    lid->enable(timeStep);
    lid->enablePointCloud();
    Gps = getGPS("gps");
    Gps->enable(timeStep);
    display = getDisplay("display");
    imu = getInertialUnit("inertial unit");
    imu->enable(timeStep);
    motors[0] = getMotor("fl");
    motors[1] = getMotor("fr");
    motors[2] = getMotor("hl");
    motors[3] = getMotor("hr");
    motors[4] = getMotor("fld");
    motors[5] = getMotor("frd");
    motors[0]->setPosition(std::numeric_limits<double>::infinity());
    motors[1]->setPosition(std::numeric_limits<double>::infinity());
    motors[2]->setPosition(std::numeric_limits<double>::infinity());
    motors[3]->setPosition(std::numeric_limits<double>::infinity());
    motors[4]->setPosition(0.0);
    motors[5]->setPosition(0.0);
    motors[0]->setVelocity(0);
    motors[1]->setVelocity(0);
    motors[2]->setVelocity(0);
    motors[3]->setVelocity(0);
}

/*小车控制*/
//四个轮子的速度和两个方向轮的速度
void Mazerobot::go(double speed1, double speed2, double speed3, double speed4, double p1 ,double p2) {
    motors[0]->setVelocity(speed1);
    motors[1]->setVelocity(speed2);
    motors[2]->setVelocity(speed3);
    motors[3]->setVelocity(speed4);
    motors[4]->setPosition(p1);
    motors[5]->setPosition(p2);
}

/*小车点到点模糊控制*/
int Mazerobot::point2point(double imu, double x_car, double y_car, double x_target, double y_target) {
    double topoint_x = x_target - x_car;
    double topoint_y = y_target - y_car;
    double angle = 0.0; 

    if (topoint_x > 0 && topoint_y > 0)
        angle = atan(topoint_y/topoint_x) - Pi/2;
    else if (topoint_x < 0 && topoint_y > 0)
        angle = atan(topoint_y/topoint_x) + Pi/2;
    else if (topoint_x < 0 && topoint_y < 0)
        angle = atan(topoint_y/topoint_x) + Pi/2;
    else if (topoint_x > 0 && topoint_y < 0)
        angle = atan(topoint_y/topoint_x) - Pi/2;

    double angle_imu;
    double speed = 10;
    angle_imu = angle - imu;
    //控制到[-Pi, Pi]之间
    if (angle_imu < -Pi) angle_imu += 2*Pi;
    if (angle_imu >  Pi) angle_imu -= 2*Pi;

    double kd = angle_imu/Pi*5;     //模糊控制量
    double basic = angle_imu > 0 ? (-angle_imu+Pi)*speed : (angle_imu+Pi)*speed;

    if (angle_imu > Pi/8) go(-20, 20, -20, 20, 0, 0);
    else if (angle_imu < -Pi/8) go(20,-20, 20, -20, 0, 0);
    //if (angle_imu > Pi/8) go(-10, 10, -10, 10, 0, 0);
    //else if (angle_imu < -Pi/8) go(10,-10, 10, -10, 0, 0);
    else go(basic, basic, basic, basic, kd, kd);
  
    if (sqrt((topoint_x * topoint_x) + (topoint_y * topoint_y)) < 0.2)
        return 1;
    return 0;
}

/*rrt路径生成*/
void Mazerobot::get_rrtroad(map &m,double x_car,double y_car) {
    int node_in_quantaty = 1;
    int min;
    rand_n[0].x = x_car;
    rand_n[0].y = y_car;
    rand_n[0].last_node = -1;
  
    rand_path[0].x = x_car;
    rand_path[0].y = y_car;
  
    //生成随机点
    for (int i=0;i<node_quantaty;i++) {
        int rand_no1 =rand() % int(width*map_rate);//注意，如果地图不一样，随机变量的范围也要改
        int rand_no2 =rand() % int(height*map_rate);
        //需要找到随机点最近的节点
        double x =  rand_no1/map_rate - width/2;//x像素点矩阵转换为真实坐标值
        double y = -rand_no2/map_rate + height/2;//y像素点矩阵转换为真实坐标值
        min = 0; //找到头结点
        double distance_n2n_first = (rand_n[0].x - x)*(rand_n[0].x - x) + (rand_n[0].y - y)*(rand_n[0].y - y);
        //计算随机点最近的节点
        for (int i=1;i<node_in_quantaty;i++) {
            double distance_n2n_other = (rand_n[i].x - x)*(rand_n[i].x - x) + (rand_n[i].y - y)*(rand_n[i].y - y);
            if (distance_n2n_other < distance_n2n_first) {
                distance_n2n_first = distance_n2n_other;
                min = i;
            }
        }
   
        //生成随机点方向的定长直线
        double theta = atan((y-rand_n[min].y)/(x-rand_n[min].x));
        if (x-rand_n[min].x < 0)
            theta = Pi + atan((y-rand_n[min].y)/(x-rand_n[min].x));
        if (x-rand_n[min].x == 0 || y-rand_n[min].y == 0)
            continue;   //这里插入节点的中心的正方形内是否与障碍物干涉的判断，如果干涉，就continue
   
        rand_n[node_in_quantaty].x = rand_n[min].x + path_length * cos(theta);
        rand_n[node_in_quantaty].y = rand_n[min].y + path_length * sin(theta);
        rand_n[node_in_quantaty].last_node = min; 
   
        double zone_x =  rand_n[min].x;
        double zone_y =  rand_n[min].y;
        int Is_Pass = 1;
        //障碍点存在以路径起点为圆心的四象图里，进行讨论
        double zone_scope = 0.2;

        //第一象限
        if (cos(theta) > 0 && sin(theta) > 0) {
            for (int i = 0; i < int(path_zone*map_rate); i++) {
                zone_y =  rand_n[min].y;
                for (int j = 0; j < int(path_zone*map_rate); j++) {
                    //这一点是障碍点
                    if (m.p[int(zone_x*map_rate+width/2*map_rate)][int(-zone_y*map_rate+height/2*map_rate)].Is_pass == false) {
                        double d_zone2min_x = zone_x - rand_n[min].x;
                        double d_zone2min_y = zone_y - rand_n[min].y;
                        //计算障碍物点到直线的投影长度和障碍点到路径的距离
                        double ty = (d_zone2min_x * path_length * cos(theta) + d_zone2min_y * path_length * sin(theta))/
                            (sqrt(path_length * cos(theta)*path_length * cos(theta) + path_length * sin(theta) * path_length * sin(theta)));
                        if ((ty < path_zone*1.1 && ty > 0)||(ty < 0 && ty > -path_zone*1.1)) {
                            double distance_zone2line = sqrt(d_zone2min_x*d_zone2min_x+d_zone2min_y*d_zone2min_y - ty*ty);
                            if (distance_zone2line < zone_scope) {
                                Is_Pass = 0;
                                continue;
                            }
                        }
                    }
                    zone_y += 0.1;
                }
                zone_x += 0.1;
            }
        }
        //第二象限
        else if(cos(theta) < 0 && sin(theta) > 0) {
            for (int i = 0; i < int(path_zone*map_rate); i++) {
                zone_y =  rand_n[min].y;
                for (int j = 0; j < int(path_zone*map_rate); j++) {
                    //这一点是障碍点
                    if (m.p[int(zone_x*map_rate+width/2*map_rate)][int(-zone_y*map_rate+height/2*map_rate)].Is_pass == false) {
                        double d_zone2min_x = zone_x - rand_n[min].x;
                        double d_zone2min_y = zone_y - rand_n[min].y;
                        //计算障碍物点到直线的投影长度和障碍点到路径的距离
                        double ty = (d_zone2min_x * path_length * cos(theta) + d_zone2min_y * path_length * sin(theta))/
                            (sqrt(path_length * cos(theta)*path_length * cos(theta) + path_length * sin(theta) * path_length * sin(theta)));
                        if ((ty < path_zone*1.1 && ty > 0)||(ty < 0 && ty > -path_zone*1.1)) {
                            double distance_zone2line = sqrt(d_zone2min_x*d_zone2min_x+d_zone2min_y*d_zone2min_y - ty*ty);
                            if (distance_zone2line < zone_scope) {
                                Is_Pass = 0;
                                continue;
                            }
                        }
                    }
                    zone_y += 0.1;
                }
                zone_x -= 0.1;
            }
        }
        //第三象限
        else if (cos(theta) < 0 && sin(theta) < 0) {
            for (int i = 0; i < int(path_zone*map_rate); i++) {
                zone_y =  rand_n[min].y;
                for (int j = 0; j < int(path_zone*map_rate); j++) {
                    //这一点是障碍点
                    if (m.p[int(zone_x*map_rate+width/2*map_rate)][int(-zone_y*map_rate+height/2*map_rate)].Is_pass == false) {
                        double d_zone2min_x = zone_x - rand_n[min].x;
                        double d_zone2min_y = zone_y - rand_n[min].y;
                        //计算障碍物点到直线的投影长度和障碍点到路径的距离
                        double ty = (d_zone2min_x * path_length * cos(theta) + d_zone2min_y * path_length * sin(theta))/
                            (sqrt(path_length * cos(theta)*path_length * cos(theta) + path_length * sin(theta) * path_length * sin(theta)));
                        if ((ty < path_zone*1.1 && ty > 0)||(ty < 0 && ty > -path_zone*1.1)) {
                            double distance_zone2line = sqrt(d_zone2min_x*d_zone2min_x+d_zone2min_y*d_zone2min_y - ty*ty);
                            if (distance_zone2line < zone_scope) {
                                Is_Pass = 0;
                                continue;
                            }
                        }
                    }
                    zone_y -= 0.1;
                }
                zone_x -= 0.1;
            }
        }
        //第四象限
        else if(cos(theta) > 0 && sin(theta) < 0) {
            for (int i = 0; i < int(path_zone*map_rate); i++) {
                zone_y =  rand_n[min].y;
                for (int j = 0; j < int(path_zone*map_rate); j++) {
                    //这一点是障碍点
                    if (m.p[int(zone_x*map_rate+width/2*map_rate)][int(-zone_y*map_rate+height/2*map_rate)].Is_pass == false) {
                        double d_zone2min_x = zone_x - rand_n[min].x;
                        double d_zone2min_y = zone_y - rand_n[min].y;
                        //计算障碍物点到直线的投影长度和障碍点到路径的距离
                        double ty = (d_zone2min_x * path_length * cos(theta) + d_zone2min_y * path_length * sin(theta))/
                            (sqrt(path_length * cos(theta)*path_length * cos(theta) + path_length * sin(theta) * path_length * sin(theta)));
                        if ((ty < path_zone*1.1 && ty > 0)||(ty < 0 && ty > -path_zone*1.1)) {
                            double distance_zone2line = sqrt(d_zone2min_x*d_zone2min_x+d_zone2min_y*d_zone2min_y - ty*ty);
                            if (distance_zone2line < zone_scope) {
                                Is_Pass = 0;
                                continue;
                            }
                        }
                    }
                    zone_y -= 0.1;
                }
                zone_x += 0.1;
            }
        }
        if (Is_Pass == 0 ) 
            continue;
        // 路径只需要记录每一个节点的上一个节点位置，最后找到目标后反推整条路径即可
        int reverse_order = 0;
        // 分叉已经找到目标节点！
        if (sqrt((rand_n[node_in_quantaty].x - target_map_x)*(rand_n[node_in_quantaty].x - target_map_x) + 
            (rand_n[node_in_quantaty].y - target_map_y)*(rand_n[node_in_quantaty].y - target_map_y)) < 0.2)  {
            //逆向搜索找全路径
            for (int i = node_in_quantaty; rand_n[i].last_node != 0; i=rand_n[i].last_node) {
                rand_path[reverse_order].x = rand_n[i].x;
                rand_path[reverse_order].y = rand_n[i].y;
                reverse_order++;
            }
            reverse_order_save = reverse_order;
            //逆转顺序表
            for (int i = 1; reverse_order >= 0 ; i++) {
                final_path[i].x = rand_path[reverse_order-1].x;
                final_path[i].y = rand_path[reverse_order-1].y;
                reverse_order--;     
            }
            final_path[0].x = x_car;
            final_path[0].y = y_car;
            //绘制地图
            for (int j = 0; j < reverse_order_save; j++)
                display->drawLine(int(final_path[j].x*map_rate+width/2*map_rate), int(-final_path[j].y*map_rate+height/2*map_rate), 
                    int(final_path[j+1].x*map_rate+width/2*map_rate), int(-final_path[j+1].y*map_rate+height/2*map_rate));
            break;  //找到后结束循环
        } 
        node_in_quantaty++;
    }
}

/*主控制函数*/
void Mazerobot::control() {
    step(timeStep);
    map m;
    point pp;
    while (step(timeStep) != -1) {
        /*制作并且保存地图*/
        const double *g = Gps->getValues();//获取小车坐标
        const double *p = imu->getRollPitchYaw();//获取小车imu位姿信息
        const LidarPoint *n = lid->getLayerPointCloud(0);//雷达点云信息
        if (t % 1 == 0) {      
            if (sqrt((g[0]-target_map_x)*(g[0]-target_map_x)+(g[1]-target_map_y)*(g[1]-target_map_y)) < 1)
                mode = FINISH;
            for (int i = 1; i < 1024; i++) {    //雷达扫描点个数
                //离群点处理：舍弃与临近点大于阈值的雷达点
                if (sqrt((n[i].x-n[i-1].x)*(n[i].x-n[i-1].x) + (n[i].z-n[i-1].z)*(n[i].z-n[i-1].z)) < 0.08) {
                    pp = m.turn_coordinate(g[0], g[1], p[0], n[i].x, n[i].z);
                    m.set_point(m.p[int(pp.x*map_rate+width/2*map_rate)][int(-pp.y*map_rate+height/2*map_rate)], false);//定义地图的墙
                    display->drawPixel(int(pp.x*map_rate+width/2*map_rate), int(-pp.y*map_rate+height/2*map_rate));//画出墙
                }
            }
        }
        if (t > 1) {
            switch(mode) {
                //规划路径，找到rrt路径
                case GET_PATH: {
                    display->setColor(0x000000);
                    for (int j = 0; j < reverse_order_save; j++)
                        display->drawLine(int(final_path[j].x*map_rate+width/2*map_rate), int(-final_path[j].y*map_rate+height/2*map_rate),
                            int(final_path[j+1].x*map_rate+width/2*map_rate), int(-final_path[j+1].y*map_rate+height/2*map_rate));
                    display->setColor(0xFFFFFF);
                    get_rrtroad(m,g[0],g[1]);
                    mode = GO;
                    break;
                }
                //走到路径的第一个节点处，重新检测路径
                case GO: {                        
                    int arrival = 0;
                    //每走一步检查一次
                    if (step_first < 2) {
                        arrival = point2point(p[0], g[0], g[1], final_path[step_first].x, final_path[step_first].y); //完成小车运动控制
                        if (arrival == 1)  step_first++;
                    }
                    else {
                        mode = GET_PATH;
                        step_first = 1;
                    }
                    break;
                }
                //抵达终点附近，直线调整到目标位置
                case FINISH: {
                    int Is_gameover = 0; 
                    Is_gameover = point2point(p[0], g[0], g[1], target_map_x, target_map_y); //调用函数直达终点
                    if (Is_gameover == 1) {
                        mode = STOP;
                        display->setColor(0x000000);
                        for (int j = 0; j < 1024; j++)
                            display->drawLine(j, 0, j, 1023);   //屏幕清为黑
                        display->setColor(0xFF0000); //屏幕输出OK
                        display->setFont("Arial", width+height, true);
                        char t1 = 'O';
                        char t2 = 'K';
                        display->drawText(&t1, 3*width, 4*height);
                        display->drawText(&t2, 5.5*width, 4*height);
                    }
                    break;
                }  
                default:
                    motors[0]->setVelocity(0.0);
                    motors[1]->setVelocity(0.0);
                    break;
            }
        }
        t++;
    }
}

int main() {
    Mazerobot *controller = new Mazerobot();
    controller->control();
    delete controller;
    return 0;
}
