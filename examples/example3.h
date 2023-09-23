#ifndef EXAMPLE3_H
#define EXAMPLE3_H


// Class declaration for Node
class Node {
public:
    Node(int data);
    void setNext(Node* nextNode);
    Node* getNext();
    int getData();
private:
    int data;
    Node* next;
};

#endif // EXAMPLE3_H
