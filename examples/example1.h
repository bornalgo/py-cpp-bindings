#ifndef EXAMPLE1_H
#define EXAMPLE1_H

#include <iostream>
#include <string>

// Enumeration
enum Color {
    RED,
    GREEN,
    BLUE
};

// Function Declarations
int add(int a, int b);
double multiply(double x, double y);
std::string greet(const std::string& name);

// Class Declaration
class Rectangle {
public:
    Rectangle(double width, double height);
    double area() const;
    double perimeter() const;
private:
    double width_;
    double height_;
};

#endif  // EXAMPLE1_H
