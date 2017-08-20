cmake_minimum_required (VERSION 2.8)
project (mydhclient)
add_executable(mydhclient mydhclient.c)
target_link_libraries(mydhclient pcap)
