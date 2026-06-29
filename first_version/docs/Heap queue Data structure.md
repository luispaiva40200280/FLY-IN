
## What is an queue ?
- A queue is a linear data structure that operates on the **FIFO (First-In, First-Out)** principle. This means that the first element added to the structure is strictly the first element to be removed, exactly like a line of people waiting at a grocery store checkout.
	- **Example:**
	Assume we have an initial queue represented as: `[1, 2, 3]` If we add the number `4` to the queue, it joins the back of the line: `[1, 2, 3, 4]` When it is time to remove an element, the computer will extract `1`.

**How it works under the hood:** In a standard array (like a basic Python `list`), removing the first element is highly inefficient because the computer must physically shift the memory addresses of every remaining element one step to the left.

To solve this, efficient queues do _not_ reverse the list in memory. Instead, they abandon standard arrays and use structures like **Linked Lists** or **Circular Buffers**. By doing this, the computer simply uses memory pointers to keep track of a "Head" and a "Tail". When an element is added or removed, the computer instantly moves the pointer rather than physically shifting the underlying data, making the operation incredibly fast for the CPU.

### What is an heap queue (priority queue)? 
- At its core, a priority queue is a data structure that replaces the standard FIFO (First-In, First-Out) rule with a priority-based system. Instead of retrieving the oldest element, it retrieves the element with the highest priority (e.g., the lowest cost).

- Under the hood, this is most commonly implemented using a **Heap**. A heap conceptually organizes data as a complete binary tree, specifically maintaining the "Heap Property": every parent node is guaranteed to be smaller than or equal to its children (in a min-heap).



![[Heapqueue_repre.webp]]

### Binary trees: 
- ****Binary Tree*** is a non-linear and hierarchical data structure where each node has **at most two children*** referred to as the left child and the right child.  The topmost node in a binary tree is called the root, and the bottom-most nodes(having no children) are called leaves.
### 1. The Anatomy of a Binary Tree
A **Binary Tree** is a hierarchical data structure. Unlike arrays or linked lists where data is arranged in a straight line, a binary tree organizes data like a corporate org chart.
It is defined by a few strict rules:
- **Node:** Every piece of data is encapsulated in a "node".
- **Root:** The absolute top node of the tree.
- **Children:** A single parent node can have a maximum of **two** children (a Left Child and a Right Child).
- **Leaves:** Nodes at the very bottom that have no children.
### 2. The Min-Heap: A Specialized Binary Tree

A Priority Queue (Heap Queue) uses a very specific type of binary tree called a **Min-Heap** (or Max-Heap). A Min-Heap enforces two additional, non-negotiable rules on the standard binary tree:

1. **The Shape Property:** The tree must be "complete." This means every level of the tree must be completely filled with nodes before starting a new level, and the bottom level must be filled from strictly left to right.
2. **The Heap Property:** A parent node must **always** be mathematically smaller than or equal to both of its children.
    

**Why not just use a sorted list?** If your pathfinder used a standard list and you wanted to insert a new path, the computer would have to compare the new path against every single item, and then physically shift thousands of memory addresses to make room. That is an O(N) operation. As the drone swarm explores thousands of nodes, the simulation would freeze.

By using a Min-Heap tree, the computer only cares about the parent/child relationships. When you add a new node, it simply drops it at the very bottom of the tree (leftmost available spot) and compares it _only_ to its direct parent. If it is smaller than its parent, they swap places (a process called "bubbling up"). It only takes a maximum of log(N) swaps to reach the top. Inserting into a heap containing 1,000,000 items takes about 20 operations, not 1,000,000
#### Terminologies in Binary Tree
- ****Parent Node****: A node that is the ****direct ancestor**** of a node(its child node).
- ****Child Node****: A node that is the ****direct descendant**** of another node (its parent).
- ****Ancestors of a node****: All nodes on the path from the root to that node (including the node itself).
- ****Descendants of a node****: All nodes that lie in the sub tree rooted at that node (including the node itself).
- ****Sub tree of a node****: A tree consisting of that node as root and all its descendants.
- ****Edge:**** The link/connection between a parent node and its child node.
- ****Path in a binary tree:**** A sequence of nodes connected by edges from one node to another.
- ****Leaf Node****: A node that does not have any children or both children are null.
- ****Internal Node****: A node that has at least one child.
- ****Depth/Level of a Node****: The number of edges in the path from root to that node. The depth/level of the ****root**** node is zero.
- ****Height of a Binary Tree****: The number of edges on the longest path from root to a leaf.