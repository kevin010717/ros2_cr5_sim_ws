#include <string>
#include <chrono>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

using namespace std;


class SimplePublisherNode: public rclcpp::Node {

public:
    SimplePublisherNode(const string& node_name)
    : Node(node_name), count_(0)
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>(
            "/simple_topic", 10);

        timer_ = this->create_wall_timer(
            1500ms, 
            std::bind(&SimplePublisherNode::timer_callback, this));

        RCLCPP_INFO(this->get_logger(), "发布节点 cpp_simple_publisher 已启动!");
    }

private:
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    size_t count_;

    void timer_callback()
    {
        auto msg = std_msgs::msg::String();
        msg.data = "id(" + std::to_string(count_++) + ") 这是一个简单的 c++ 发布节点!";
        publisher_->publish(msg);
        RCLCPP_INFO(this->get_logger(), "发布消息: %s", msg.data.c_str());
    }
};


int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SimplePublisherNode>("cpp_simple_publisher");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
