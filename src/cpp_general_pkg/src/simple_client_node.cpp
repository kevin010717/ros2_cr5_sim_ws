#include <string>
#include <chrono>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <example_interfaces/srv/add_two_ints.hpp>

using namespace std;


class SimpleClientNode: public rclcpp::Node {

public:
    SimpleClientNode(const string& node_name) 
    : Node(node_name) 
    {
        client_ = create_client<example_interfaces::srv::AddTwoInts>(
            "/cpp_simple_service");

        while (!client_->wait_for_service(1.5s))
        {
            RCLCPP_WARN(get_logger(), "服务未就绪，请稍等...");
        }
    }

    void call_service(int a, int b) {
        auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
        request->a = a;
        request->b = b;

        auto future = client_->async_send_request(request);
        RCLCPP_INFO(get_logger(), "发出请求: a=%ld + b=%ld", request->a, request->b);

        if (rclcpp::spin_until_future_complete(shared_from_this(), future) 
            == rclcpp::FutureReturnCode::SUCCESS) 
        {
            RCLCPP_INFO(
                get_logger(), "收到响应: %ld + %ld = %ld",
                request->a, request->b, future.get()->sum);
        } 
        else 
        {
            RCLCPP_ERROR(get_logger(), "请求失败!");
        }
    }

private:
    rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SimpleClientNode>("cpp_simple_client");
    int a = 0;
    int b = 1;
    while (true)
    {
        node->call_service(a, b);
        a += 1;
        b += 3;
        this_thread::sleep_for(chrono::seconds(1));
        if (a > 10) { 
            break; 
        }
    }

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
