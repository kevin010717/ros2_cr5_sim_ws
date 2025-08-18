cmake_minimum_required(VERSION 3.8)
project(cpp_general_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(example_interfaces REQUIRED)

# 创建可执行文件
add_executable(simple_node src/simple_node.cpp)
add_executable(simple_publisher_node src/simple_publisher_node.cpp)
add_executable(simple_subscriber_node src/simple_subscriber_node.cpp)
add_executable(simple_server_node src/simple_server_node.cpp)
add_executable(simple_client_node src/simple_client_node.cpp)

# 添加依赖
ament_target_dependencies(simple_node rclcpp)
ament_target_dependencies(simple_publisher_node rclcpp std_msgs)
ament_target_dependencies(simple_subscriber_node rclcpp std_msgs)
ament_target_dependencies(simple_server_node rclcpp example_interfaces)
ament_target_dependencies(simple_client_node rclcpp example_interfaces)

# 安装可执行文件
install(TARGETS simple_node DESTINATION lib/${PROJECT_NAME})
install(TARGETS simple_publisher_node DESTINATION lib/${PROJECT_NAME})
install(TARGETS simple_subscriber_node DESTINATION lib/${PROJECT_NAME})
install(TARGETS simple_server_node DESTINATION lib/${PROJECT_NAME})
install(TARGETS simple_client_node DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
