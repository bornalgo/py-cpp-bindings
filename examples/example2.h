#ifndef EXAMPLE2_H
#define EXAMPLE2_H

#include <iostream>

// Function declarations
int subtract(int x, int y);
float divide(float a, float b);

// Enum declaration
enum Fruit {
    APPLE,
    BANANA,
    ORANGE
};

// Class declaration
class Animal {
public:
    Animal();
    Animal(const std::string& name, int age);
    void printInfo();
private:
    std::string name;
    int age;
};

#endif // EXAMPLE2_H
