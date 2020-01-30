function [offset] = calculate_cr_offset(start_time_txt)
%CALCULATE_CR_OFFSET Summary of this function goes here
%   Detailed explanation goes here

fileID = fopen(start_time_txt, 'r');

radar_time_str = split(fgetl(fileID));
radar_time_str = split(radar_time_str{2}, ':');
radar_time = str2num(radar_time_str{end});

camera_time_str = split(fgetl(fileID));
camera_time_str = split(camera_time_str{2}, ':');
camera_time = str2num(camera_time_str{end});

offset = round((camera_time - radar_time) * 30) + 40;

end

