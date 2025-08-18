#include <string>

#include <rclcpp/rclcpp.hpp>
#include <example_interfaces/srv/add_two_ints.hpp>

using namespace std;
using std::placeholders::_1;
using std::placeholders::_2;


class SimpleServerNode: public rclcpp::Node {

public:
    SimpleServerNode(const string& node_name)
    : Node(node_name)
    {
        service_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            "/cpp_simple_service",
            std::bind(&SimpleServerNode::callback, this, _1, _2));

        RCLCPP_INFO(this->get_logger(), "服务节点 cpp_simple_server 已启动!");
    }

private:
    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;

    void callback(
        const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
        std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
    {
        response->sum = request->a + request->b;

        RCLCPP_INFO(this->get_logger(), "收到请求: a=%ld, b=%ld", request->a, request->b);
        RCLCPP_INFO(this->get_logger(), "返回响应: sum=%ld", response->sum);
    }
};


int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SimpleServerNode>("cpp_simple_server");
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
