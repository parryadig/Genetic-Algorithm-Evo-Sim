## GA Evolution Simulator

Evolution simulator based on a genetic algorithm.

Simply download and run evo-sim.py to start simulation.


### Premise

This simulation aims to crudely model natural selection.
A fixed number of agents spawn into an environment containing both food and poison.
If they eat food, they gain health. If they eat poison, they lose health. Additionally, all agents lose health at a fixed rate.

Initially, each individual agent has no idea that eating food & avoiding poison are beneficial. The population learns this over time.

The figure below is taken at the start of simulation. The population is comprised of agents that see food and poison at random distances.
Some may be attracted to poison, others to food. Some may be attracted or repelled by both.
![ScreenShot](/1.png)

Favourable traits propagate through the generations until the entire population looks similar, as seen below.
![ScreenShot](/2.png)
Favourable traits are as follows:
  - High vision radius for food
  - Low vision radius for poison
  - Prioritises avoiding poison over eating food (as eating poison results in  -40 health and eating food results in +20)
  - Strong attraction to food
  - Strong repulsion to poison
  - High max velocity

#### Keyboard shortcuts

| Key    | Function             |
|---------------|-------------------------|
| P        | Print fittest agent in generation  |
| O          | Print fittest agent so far|
| \+        | Speed up simulation|
| \-        | Slow down simulation| 
|LMB | Show attributes for agent|


### Agent attributes

| Attribute     | Description                                                                                                                           |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------|
| max_hp        | Starting health of agent                                                                                                              |
| hp            | Current health of agent                                                                                                               |
| food_pref     | What the agent prioritises,<br>if food_pref > 0.5 then agent prioritises food<br>otherwise the agent prioritises poison               |
| food_desire   | What the agent does when it sees food,<br>if food_desire > 0.5 then the agent seeks<br>otherwise the agent either flees or wanders    |
| poison_desire | What the agent does when it sees poison,<br>if poison_desire > 0.5 then the agent seeks<br>otherwise the agent either flees or wander |
| food_vision   | Radius at which agent can see food                                                                                                    |
| poison_vision | Radius at which agent can see poison                                                                                                  |
| max_vel       | Maximum speed of agent  


### Mutation

Chance of mutation during reproduction is controlled by MUTATION_CHANCE variable. 
```python
for i in range(len(dna) - 1):
    new_dna[i] *= random.uniform(0.9, 1.1)
    if isinstance(dna[i], int):
        new_dna[i] = math.floor(new_dna[i])
```
If mutation occurs, each attribute is scaled by a random value between 0.9 and 1.1 (for a maximum change of +/- 10%)


