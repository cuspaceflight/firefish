% Shear Modulus
G = 2.62 * 10^9;

%%%%%%%%%%%%%%%%%%%%% Fin dimensions %%%%%%%%%%%%%%%%%%%%%%
%all values in cm

%root chord
cr = 20;
%tip chord
ct = 10;
%semi span
b = 10;
%thickness
t = 0.2;

%%%%%%%%%%%%%%%%%   Derived dimensions %%%%%%%%%%%%%%%%%%%%%%%

%Area
S = 0.5 * (cr + ct) * b;
% Aspect ratio
Ra = b*b / S;
% Taper ratio
k = ct / cr;

%%%%%%%%%%%%%% Derive sound velocity and pressure for different altitudes %%%%%%%%%%%%%

%altitude matrix;
z = 0:10:50000;
z_km = z./1000;

N = size(z, 2);

%pressure
P = zeros(1, N);
%local temperature
T = zeros(1, N);
%local speed of sound
a = zeros(1, N);

for i=1:N
    % Troposphere
    if(z(i) <= 11000) 
        T(i) = 15.04 - 0.00649 * z(i);
        P(i) = 1000 * 101.29 * ( (T(i) + 273.1)/288.08 )^5.256;
    end
    
    %Lower Stratosphere
    if( (z(i) > 11000) && (z(i) <= 25000) )
        T(i) = -56.46;
        P(i) = 1000 * 22.65 * exp(1.73 - 0.000157 * z(i));
    end
    
    %Upper Stratosphere
    if( z(i) > 25000 ) 
        T(i)  =-131.21 + 0.00299 * z(i);
        P(i) = 1000 * 2.488 * ( (T(i) + 273.1) / 216.6 )^-11.388;
    end
    
    %from Hyperphysics
    a(i) = 331.3 * sqrt(1 + (T(i) / 273.15));
end

%%%%%%%%%%%  Calculate the flutter velocity %%%%%%%%%%%%%%%%%%%%%%%%%%

Vf = zeros(1, N);

for i = 1:N
    %intermediate values
    A = 1.337 * Ra^3 * P(i) * (k+1);
    B  = 2 * (Ra + 2) * (t/cr)^3;
    
    Vf(i) = a(i) * sqrt(G*B /A);
end

%%%%%%%%%%%%%%%%%% Plot %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
figure
plot(z_km, Vf);

title('Flutter velocity vs altitude');
xlabel('altitude/km');
ylabel('flutter velocity / ms-1');




