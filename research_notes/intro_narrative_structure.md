# Intro Narrative Structure

Date: 2026-05-20

## Core Positioning

The reinforcement-learning, vision, and grasping motivation should appear as long-term motivation, not as a claimed contribution of this paper. The paper's actual contribution is narrower: to make future simulation-based learning and control more credible, first identify and model the gap between a fast flapping-wing aerodynamic simulator and real outdoor flight.

In other words, the story should not be "this paper trains an RL controller." It should be "future RL and interaction-rich tasks need a useful simulator, and this paper builds one important part of that simulator by diagnosing and correcting real-flight aerodynamic mismatch."

## Recommended Storyline

### 1. Start from the need for high-fidelity simulation

Future flapping-wing aerial vehicles may need to do more than stabilize flight. They may need to combine flight control with perception, target interaction, grasping, perching, or other task-level objectives. Reinforcement learning is attractive for these settings because it can incorporate flight states, vision, contact information, and task rewards in one training framework.

However, reinforcement learning requires large amounts of interaction data. Training directly on hardware is costly, risky, and difficult to scale, especially when failure cases and broad operating conditions are needed.

### 2. Explain why real flight logs alone are not enough

Real flight logs are valuable because they contain the actual vehicle response, real actuator behavior, outdoor disturbances, and sensing effects. They can support offline learning or system identification.

The limitation is coverage. Flight logs mainly cover the state distribution that has already been flown successfully. If strong generalization is required, the dataset would need to include many operating conditions, aggressive maneuvers, disturbances, and failure cases. Collecting that coverage on real hardware is expensive and risky. This motivates simulation-based training and evaluation.

### 3. State that flapping-wing simulation depends on aerodynamic modeling

A useful simulator needs dynamics, and for flapping-wing vehicles the hard part is aerodynamic force and moment modeling. The forces come from periodic wing motion, flexible wings, tail effects, body-wing coupling, and unsteady flow.

Common modeling choices include CFD, UVLM or vortex-based methods, and empirical or semi-empirical models. CFD can be accurate but is too slow for large-scale simulation and reinforcement learning. UVLM is a middle ground but can still be computationally heavy. Empirical models such as DeLaurier-style formulations are much faster and physically structured, making them practical as simulator priors.

### 4. Introduce sim-to-real gap as the central problem

Fast empirical models are useful, but their assumptions and parameters do not fully match a real vehicle. The gap can come from wing flexibility, mechanism timing, actuator dynamics, tail effectiveness, fuselage effects, wind, sensor alignment, and state-estimation errors.

Domain randomization can improve robustness during reinforcement learning, but it is not a complete substitute for understanding systematic aerodynamic mismatch. If a large part of the sim-to-real gap comes from the aerodynamic prior itself, then the simulator should first be calibrated and its residual error should be diagnosed.

### 5. Explain why the platform makes this study natural

Previous work and engineering practice show that flapping-wing vehicles can often fly with control ideas adapted from fixed-wing aircraft. Our platform can fly using a PX4-based fixed-wing stack and can record synchronized flight logs, including state estimates, airspeed, actuator commands, flapping phase, and flapping frequency.

This makes it natural to use real flight logs to ask a simulator-focused question: given a fast DeLaurier-style aerodynamic model, where does its predicted wrench differ from the effective wrench observed in real flight?

### 6. Close with what this paper actually does

This paper does not directly train a reinforcement-learning controller. Instead, it builds a data-driven correction layer for a physically structured simulator prior.

The paper reconstructs body-frame six-axis effective wrench labels from outdoor flight logs, aligns them with a DeLaurier-style flapping-wing aerodynamic model, calibrates the physical model using training logs, and trains a causal neural residual model to predict the remaining discrepancy. The residual is then analyzed by wingbeat phase, flapping frequency, and flight condition to determine whether the simulator mismatch is structured rather than random.

## Suggested English Framing

> While reinforcement learning offers a natural framework for future flapping-wing tasks involving perception and interaction, training such policies directly on hardware is costly and difficult to generalize. Simulation is therefore essential, but its usefulness depends on the fidelity of the underlying flapping-wing dynamics. Fast empirical aerodynamic models provide a practical simulator prior, yet their mismatch to real free flight remains a major source of sim-to-real gap. This motivates using real flight logs not merely to train a black-box model, but to diagnose and correct the residual between a structured aerodynamic simulator and the effective wrench observed in flight.

## Writing Notes

Keep the RL, vision, and grasping motivation short. These ideas justify why simulation matters, but the paper does not evaluate those tasks.

Mention domain randomization carefully. The point is not that domain randomization is ineffective, but that it benefits from a physically meaningful simulator prior and from knowing which aerodynamic errors are systematic.

The PX4/fixed-wing-stack point should be used as a bridge to available real flight logs, not as a major related-work claim.

The final intro should make the paper's contribution clear: real-flight effective-wrench reconstruction, DeLaurier-style simulator-prior calibration, causal neural residual correction, and residual-structure analysis.
