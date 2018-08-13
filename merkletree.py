import hashlib

class MerkleTree:
    """
        `The Merkle Tree is a special kind of Binary Tree that allows the user to prevent 
        information malleability and preserve integrity by using cryptographically secure
        hash functions. By providing leaves you create a root by concatination and hashingself.
        If the root is mutated it means that the data inside the leaves was changed. You can also
        derive cryptographic proofs that a piece of data is inside the tree`

        Comments:
           Complexities - This part can be improved by doing couple of modifications 
    """


    class __Node:

        def __init__(self, item=None, left=None, right=None):
            """
            `Merkle Node constructor. Used for storing the left and right node pointersself.`

            Args:
                item (bytes): Bytes object that represents the hashed value that resides in the current node
                left (Node): Reference to the left subtree or a None value if current node is leaf
                right (Node): Reference to the right subtree or a None value if current node is leaf
            """
            self.left = left
            self.right = right
            self.__value = item
            self.parent = None
            self.pos = -1

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self, value):
            self.__value = value

        def __str__(self):
            return 'Value: {0}'.format(self.value)
        
        def __repr__(self):
            return self.__str__() + '\n\t' + self.left.__repr__() + '\n\t' + self.right.__repr__()

    
    def __init__(self,
                 iterable,
                 digest_delegate=lambda x: str(x)):
        """
            `Merkle Tree constructor`
        
            Args:
                iterable (list_iterator): The collection you want to create the root from
                digest_delegate (function): ~
                  ~ A delegate (reference to function) that returns the digest of a passed in argument
        """
        if not iterable:
            raise Exception("iterable cannot be empty.")
        self.digest = digest_delegate
        self.__root = self.build_root(iterable)
  
    @property
    def root(self):
        return self.__root

    def build_root(self, iterable):
        """
            `This method builds a Merkle Root from the passed in iterable.
             After the data is preprocessed, it calls the internal __build_root
             function to build the actual Merkle Root.`
            
            Args:
                iterable (list_iterator): The collection you want to create the root from
            
            Returns:
                Node: The newly built root of the Merkle Tree
        """

        if len(iterable) == 1:
            return iterable[0]

        if len(iterable) % 2 != 0:
            #print(f"Duplicated Last item: {iterable[-1][0:5]+'...'}")
            iterable.append(iterable[-1])

        # subdivides the list into pairs
        data = [iterable[n:n+2] for n in range(0, len(iterable), 2)]
        print(data)
        return self.build_root([self.join(*arg) for arg in data])


    def join(self, x, y):
        #return hashlib.sha256((str(x) + str(y)).encode()).hexdigest()
        if type(x) == str or type(x) == int:
            x = self.__Node(item=self.digest(x))
            y = self.__Node(item=self.digest(y))
        #print(x, y)
        if type(x.value) == bytes:
            value_x = x.value
            value_y = y.value
        else:
            value_x = x.value
            value_y = y.value

        node = self.__Node(item=self.digest(value_x+value_y),
                           left=x,
                           right=y)
        x.parent = node
        y.parent = node
        x.pos = 0
        y.pos = 1
        return node
        # Return the root

    def contains(self, value):
        """
            `The contains method checks whether the item passed in as an argument is in the
            tree and returns True/False. It is used only externally. It's internal equivalent
            is __find`

            Args:
                value (object): The value you are searching for

            Returns:
                bool: The result of the search

            Complexity:
                O(n)
        """
        if value is None or self.root is None:
            return False

        hashed_value = self.digest(value)

        return self.__find(self.root, hashed_value) is not None 

    def __find(self, node, value):
        """
            `Find is the internal equivalent of the contains method`

            Args:
                value (object): The value you are searching for

            Returns:
                bool: The result of the search

            Complexity:
                O(n)
        """
        if node is None:
            return None

        if node.value == value:
            return node
        
        return self.__find(node.left, value) or self.__find(node.right, value)

    def request_proof(self, value):
        """
            `The request_proof method provides to the caller a merkle branch in order to prove
            that the integrity of the data is in tact. The caller can use the same digest and 
            verify it himself`

            Args:
               value (object) - The item you want proof for

            Returns:
               list - Python list containing the merkle branch (proof) in the form of tuples

            Throws:
                Exception - On invalid value or one that is not contained in the tree
        """
        # TODO: Implement this method
        # Try implementing this method yourself. It is not mandatory though. There is a 
        # step by step solution in the exercise document

        # Hash the value
        value = self.digest(value)
        # Check if it is contained within the tree
        def in_tree(value, node):
            print(str(node))
            if node == None:
                return False
            if node.value == value:
                return node
            result = None
            result = in_tree(value, node.left)
            if not result:
                result = in_tree(value, node.right)

            if result:
                return result

            if node.left == None and node.right == None:
                return False
            return False

        node = in_tree(value, self.root)
        print(f"In tree {node}")

        if not node:
            raise Exception("Value not in tree")

        def traverse(value, node, _list=[]):
            print(str(node), _list)
            if node.pos == -1:
                print("Is root node")
                #if node.left.value == value:
                #    _list.append((1, node.value))
                #if node.right.value == value:
                #    _list.append((0, node.value))
                #_list = list(reversed(_list))

                #_list.insert(0, _list[-1])
                #_list.pop()
                #print(_list)
                return _list

            # if node.left:
            #     if node.left.value == value:
            #         _list.append((0, node.right.value))

            # if node.right:
            #     if node.right.value == value:
            #         _list.append((1, node.left.value))

            if node.value == value:
                if node.pos == 0:
                    if node.parent.right != value:
                        _list.append((0, node.parent.right.value))

                if node.pos == 1:
                    if node.parent.left != value:
                        _list.append((1, node.parent.left.value))
                
                if len(_list) == 1 and node.pos == 0:
                    _list.insert(0,(1, value))
                if len(_list) == 1 and node.pos == 1:
                    _list.append((0, value))
                    

            return traverse(node.parent.value, node.parent, _list)


        return traverse(value, node)
        
        
    def dump(self, indent=0):
        
        if self.root is None:
            return

        self.__print(self.root, indent)

    def __print(self, node, indent):
        
        if node is None:
            return

        print('{0}Node: {1}'.format(' '*indent, node.value))    
        self.__print(node.left, indent+2)
        self.__print(node.right, indent+2)

    def __contains__(self, value):
        hashed_value = self.digest(value)
        return self.__find(self.root, hashed_value)

        
        
