#include <string>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

using namespace std;
using std::placeholders::_1;


class SimpleSubscriberNode: public rclcpp::Node {

public:
    SimpleSubscriberNode(const string& node_name)
    : Node(node_name)
    {
        subscription_ = this->create_subscription<std_msgs::msg::String>(
            "/simple_topic", 10, 
            std::bind(&SimpleSubscriberNode::callback, this, _1));

        RCLCPP_INFO(this->get_logger(), "订阅节点 cpp_simple_subscriber 已启动!");
    }

private:
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;

    void callback(const std_msgs::msg::String::SharedPtr msg) const
    {
        RCLCPP_INFO(this->get_logger(), "订阅消息: %s", msg->data.c_str());
    }
};


int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SimpleSubscriberNode>("cpp_simple_subscriber");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
