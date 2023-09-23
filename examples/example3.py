import ctypes

# Structure for Node [class] (Pre-definition)
class Node(ctypes.Structure):
    pass

# Structure for Node [class] (Post-definition)
Node._fields_ = [
                 # Function type for void Node::setNext(Node * nextNode) [member function]: void ( ::Node::* )( ::Node * )
                 ("setNext", ctypes.CFUNCTYPE(
                                              None,     # void Node::setNext(Node * nextNode) [member function]: void ( ::Node::* )( ::Node * )
                                              ctypes.POINTER(Node),     # Node *: Node*
                                              )), 
                 # Function type for Node * Node::getNext() [member function]: Node * ( ::Node::* )(  )
                 ("getNext", ctypes.CFUNCTYPE(
                                              ctypes.POINTER(Node),     # Node * Node::getNext() [member function]: Node * ( ::Node::* )(  )*
                                              )), 
                 # Function type for int Node::getData() [member function]
                 ("getData", ctypes.CFUNCTYPE(
                                              ctypes.c_int,     # int Node::getData() [member function]: int ( ::Node::* )(  )
                                              )), 
                 ("data", ctypes.c_int),     # Type for Node::data [variable]
                 ("next", ctypes.POINTER(Node)),     # Type for Node::next [variable]: Node*
                 ]
