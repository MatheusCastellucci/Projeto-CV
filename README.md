<a href="https://github.com/MatheusCastellucci/Projeto-CV">
    <img src="FFVI\imgs\logo.png" alt="FF6 logo" title="Magitek" align="right" width="15%" height="15%" />
</a>

# FF6 Environment Segmentation

This project was developed for the Computer Vision course at Insper. The goal was to implement an environment segmentation algorithm for the game Final Fantasy VI. We selected this game due to its simple and well-defined art style, which facilitates the segmentation of the environment from the characters. By leveraging OpenCV and Python, we successfully created a program capable of generating a game environment for bots to learn from.

# Table of contents

- [Installation](#Installation)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Discarded Concepts](#discarded-concepts)
- [References](#references)
- [Team](#team)
  
# Installation

This library was made using Python 3.8. So make sure you have it installed.
```bash
python3 --version
pip3 --version
```

### Windows
1. Open Command Prompt or PowerShell.
2. Execute the following commands:

```sh
cd \path\to\desired\directory
git clone https://github.com/MatheusCastellucci/Projeto-CV
```

### Linux/macOS
1. Open the Terminal.
2. Execute the following commands:

```sh
cd /path/to/desired/directory
git clone https://github.com/MatheusCastellucci/Projeto-CV
```

Replace `\path\to\desired\directory` or `/path/to/desired/directory` with the path to the directory where you want to clone the repository.

These commands will create a new folder named `Projeto-CV` in the specified directory, containing all the files from the repository.

#### Once you have cloned the repository, you can install the required libraries by running the following command:
```bash
pip install -r requirements.txt
```

# Usage
Our project consists of several functions, seprated betweenn two Python file. For each function, we have a corresponding Jupyter notebook containing the implementations and a dictionary of possible test images. Additionally, we have a function that consolidates all these implementations and performs all the necessary tasks. In the repository, there is a Python file called main.py, where you can see an example of using this consolidating function.

For the Jupyter section, we adopted a simple naming convention to differentiate discarded ideas from the final functions. Files that start with “prototype” contain abandoned or incomplete ideas developed throughout the project, while files that start with “Test” are tests of the final versions where you can make any modifications you want.

# How it works
The project was designed with the aim of using classical computer vision techniques to address the challenges we would encounter. Thus, there was a significant focus on image segmentation and contour detection. Initially, our goal was to determine the current state of the game, which would allow us to extract various information from it, such as the possible actions the player could take at the exact moment, their location, among other information.

The first step was to distinguish what was on the game screen. Were we in a combat screen? An exploration screen? Or just a cutscene? To identify the state, we took advantage of the game's graphical limitations due to its release period, which made screen segmentation easier. With this, we were able to determine the current state of the game.

With the information about the game state in hand, the next step was to extract information from it. To do this, we divided the game into three states: Exploration, Combat, and Cutscene. Each state required a different approach to obtain the necessary information.

1. Exploration: In this state, the player can move freely around the map and interact with objects and NPCs. To obtain the necessary information, we applied a color filter to identify what would be considered the ground. This involved identifying the predominant colors of the ground and detecting the color of the pixels just below the characters. With this information, we created a mask that separated the ground from the characters, allowing us to know where the player was and where they could move.

2. Combat: During combat, the player faces enemies. To obtain the relevant information, we cropped the screen to capture only the combat Heads-Up Display (HUD). This allowed us to identify the actions available to the player, as well as the enemies on the screen, among other information.

3. Cutscene: During cutscenes, the player watches a sequence of events. To extract the necessary information, we applied a filter that searched for the characteristic text box of the game. This allowed us to identify the dialogue in the cutscene, as well as the possible conversation options available to the player.

With this information, we were able to determine the current state of the game and extract information from it, creating an environment where bots can learn to play the game.

### Here are some examples of each state:
<div style="display: flex;">
    <div style="flex: 1; margin-right: 100px;">
        <h3 style="font-size: 14px;">1.Exploration</h3>
        <img src="FFVI\Maps\planicie.jpg" >
    </div>
    <div style="flex: 1; margin-right: 10px;">
        <h3 style="font-size: 14px;">2.Combat</h3>
        <img src="FFVI\Combat\combate.jpg" width="77%" height="77%">
    </div>
    <div style="flex: 1; margin-right: 10px;">
        <h3 style="font-size: 14px;">3.Cutscene</h3>
        <img src="FFVI\Dialog\textbox_with_img.png" width="77%" height="77%">
    </div>
</div>

# Discarded Concepts
Originally, for the exploration part, we planned to identify the player's position on the map and, from there, determine which parts of the map are accessible. To achieve this goal, we tested different methods, including template matching and machine learning. Unfortunately, we were not successful with any of these approaches.

### Challenges with Template Matching
With 16 different characters, each having distinct sprites for their movements, template matching proved unfeasible due to the vast variation of sprites.

### Machine Learning Approach
For the machine learning approach, we created a web scraper to download GIFs of playable characters, using the site videogamesprites.net as a source. We then trained a ResNet-50 model to identify these characters in images. However, during testing, the model failed to identify any characters.

### Improvement Attempts
To improve results, we tried augmenting the training data by distorting the GIFs to handle images of different proportions and introduced Gaussian noise into the model. Despite these attempts, the model remained unable to identify the characters.

### Alternative Method
Additionally, we developed a code that crops the central region of an image, draws a colored rectangle at the position where the player is usually found (typically in the center of the image, but with variations), and identifies the three most predominant colors in the image, disregarding the color of the drawn rectangle. Initially, we planned to use these colors to create a comparison profile and decide which transformations to apply to the image. However, we decided to abandon this idea in favor of comparing the obtained histogram.

Since we could not find the playable characters, despite having extensive training data, we eventually abandoned the idea of finding non-playable characters as well.

# References

- Site from which we took most of the images and templates used for our tests: [Final Fantasy VI](https://www.videogamesprites.net/FinalFantasy6/Party/)

# Team
- [Bruno Freitas](https://github.com/BrunoFNRodrigues)
- [Carlos Eduardo](https://github.com/KdSimodo)
- [Matheus Castellucci](https://github.com/MatheusCastellucci)