# Project Vajra: Phase 1 - Software Simulation

**Lead Research Engineer**: Antigravity  
**Objective**: Demonstrate the transition of programmable matter from a 'Liquid' state to a 'Solid' state using granular jamming and hexagonal geometry.

## Overview
This simulation models a swarm of 100+ agents that exhibit two distinct states:
1.  **Liquid State**: Agents move organically using Boids flocking algorithms (Cohesion, Separation, Alignment). They behave like a fluid or loose sand.
2.  **Solid State (Jammed)**: Upon receiving a "Vacuum Signal" (triggered by mouse interaction), agents lock into a rigid hexagonal grid, simulating the phase transition of granular jamming.

## Installation

### Prerequisites
- Python 3.x
- `pygame` library

### Setup
1.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
2.  Activate the environment and install dependencies:
    ```bash
    ./venv/bin/pip install pygame
    ```
3.  Run the simulation:
    ```bash
    ./venv/bin/python main.py
    ```

## Physics Rules & Logic

### 1. The Agents (Hexagons)
- Each agent is treated mathematically as a hexagon.
- They possess position, velocity, and a state flag (`is_solid`).

### 2. Liquid Physics (Boids)
- **Separation**: Steer to avoid crowding local flockmates.
- **Alignment**: Steer towards the average heading of local flockmates.
- **Cohesion**: Steer to move towards the average position (center of mass) of local flockmates.
- **Boundary Wrapping**: Agents wrap around the screen edges to simulate a continuous volume.

### 3. Solid Physics (Jamming)
- **The Trigger**: A mouse click and drag acts as the "Vacuum Signal".
- **Locking**: When an agent touches the signal or a solidified neighbor, it snaps to the nearest vertex of a global hexagonal grid.
- **Consensus**: Solidified agents propagate the "lock" state to their neighbors, creating a growing crystal structure.
- **Indra's Net**: Visual connections (lines) are drawn between solidified neighbors to visualize the structural lattice.

## Controls
- **Mouse Left Click & Drag**: Apply "Vacuum Signal" to jam agents into solid state.
- **R Key**: Reset simulation to initial Liquid state.
- **Esc / Close Window**: Quit simulation.

## Philosophical Goal
**Simulating Algorithmic Stiffness**: This project explores how local interaction rules can lead to global phase transitions, mimicking the behavior of "smart sand" or programmable matter that can change its material properties on demand.
