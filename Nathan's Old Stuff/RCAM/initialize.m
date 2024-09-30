function initialize()
clear;
clc;
close all;

x0 = [85;
      0;
      0;
      0;
      0;
      0;
      0;
      0;
      0];

u0 = [0;
      -0.1;
      0;
      0.05;
      0.05;];

TF = 60;

out = sim('rcam.slx');

t = out.tout;

u1 = out.simU.Data(:,1);
u2 = out.simU.Data(:,2);
u3 = out.simU.Data(:,3);
u4 = out.simU.Data(:,4);
u5 = out.simU.Data(:,5);

x1 = out.simX.Data(:,1);
x2 = out.simX.Data(:,2);
x3 = out.simX.Data(:,3);
x4 = out.simX.Data(:,4);
x5 = out.simX.Data(:,5);
x6 = out.simX.Data(:,6);
x7 = out.simX.Data(:,7);
x8 = out.simX.Data(:,8);
x9 = out.simX.Data(:,9);

figure
subplot(5, 1, 1);
plot(t, u1);
legend('u1 Aileron Deflection Angle');
grid on

subplot(5, 1, 2);
plot(t, u2);
legend('u2 Elevator Deflection Angle');
grid on

subplot(5, 1, 3);
plot(t, u3);
legend('u3 Rudder Deflection Angle');
grid on

subplot(5, 1, 4);
plot(t, u1);
legend('u4 Throttle 1');
grid on


subplot(5, 1, 5);
plot(t, u5);
legend('u5 Throttle 2');
grid on

figure
subplot(3, 3, 1);
plot(t, x1);
legend('x1 Vx');
grid on

subplot(3, 3, 4);
plot(t, x2);
legend('x2 Vy');
grid on

subplot(3, 3, 7);
plot(t, x3);
legend('x3 Vz');
grid on

subplot(3, 3, 2);
plot(t, x4);
legend('x4 wx');
grid on

subplot(3, 3, 5);
plot(t, x5);
legend('x5 wy');
grid on

subplot(3, 3, 8);
plot(t, x6);
legend('x6 wz');
grid on

subplot(3, 3, 3);
plot(t, x7);
legend('x7 phi bank');
grid on

subplot(3, 3, 6);
plot(t, x8);
legend('x8 theta pitch');
grid on

subplot(3, 3, 9);
plot(t, x9);
legend('x9 psi yaw');
grid on

end



