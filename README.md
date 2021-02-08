# Gradient Based Force Field Analysis (GraFFan)

[![tests](https://github.com/SimonBoothroyd/graffan/workflows/CI/badge.svg?branch=main)](https://github.com/SimonBoothroyd/graffan/actions?query=workflow%3ACI)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/SimonBoothroyd/graffan.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/SimonBoothroyd/graffan/context:python)
[![codecov](https://codecov.io/gh/SimonBoothroyd/graffan/branch/main/graph/badge.svg?token=Aa8STE8WBZ)](https://codecov.io/gh/SimonBoothroyd/graffan)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This framework aims to offer a set of common utilities for analyzing the outputs of force field optimization (performed 
by [ForceBalance](https://github.com/leeping/forcebalance)), with a focus on providing tools for inspecting the many 
contributions to the gradient of the objective function. 

## Installation

The package and its dependencies can be installed using the `conda` package manager:

```
conda env create --name graffan --file devtools/conda-envs/test_env.yaml
python setup.py develop
```

## Getting Started

The framework offers two CLI utilities which encapsulate most of this frameworks features: `graffan analyse` and 
`graffan visualise FILENAME`.

The `graffan analyse` command should be run in the root directory of a force balance optimization and will analyze the 
outputs of each fitting target used in the optimization. Namely, it will create a new `iteration_0000.json` file (or 
similar depending on whether the `--iteration X` flag was used) which contains the contributions of each target to the 
total gradient of the objective function with respect to the force field parameters which were refit.

The `graffan visualise iteration_0000.json` command will then open up of GUI in a webbrowser allowing the extracted 
gradients to be viewed in higher detail.

## Copyright

Copyright (c) 2020, Simon Boothroyd
