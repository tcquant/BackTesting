// #include <ql/quantlib.hpp>
// #include <iostream>

// int main() {
//     QuantLib::Date date(15, QuantLib::Month::September, 2024);
//     std::cout << "Date: " << date << std::endl;
//     return 0;
// }

#include <boost/algorithm/string.hpp>
int main() {
    std::string s = "hello world";
    boost::to_upper(s);
    std::cout << s << std::endl;
    return 0;
}
