# AI Final Project

This project demonstrates the application of multi-agent search algorithms in a competitive environment by optimizing the performance of iRobots in a room-cleaning task. The goal is to design autonomous agents (iRobots) that can navigate and clean a shared space efficiently, reducing redundant actions and maximizing overall cleaning performance. The scenario mimics real-world tasks, such as household cleaning, while exploring the strategic dynamics of multi-agent systems—a key area in robotics and artificial intelligence.

## Key Features

- **Multi-Agent Environment**: Two competing iRobots operate in a shared space, aiming to achieve the highest cleaning efficiency.
- **Algorithms Used**:
  - **Minimax with Alpha-Beta Pruning**: Enhances decision-making by reducing unnecessary computations.
  - **Q-Learning**: Implements reinforcement learning for adaptive and intelligent decision-making.
- **Time Management**: Ensures timely and efficient task execution by the robots.

## How to Execute

To run the project, use the following command:

```bash
python main.py -player1 LivePlayer -player2 SimplePlayer
