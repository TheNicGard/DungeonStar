---
title: A Manual for Finding the Dungeon Star
author: Nic Gard
date: Last updated September 21, 2019
...
\pagebreak
# Introduction

This manual which you hold your hands is meant to guide you through the treacherous, far-reaching depths of the dungeon known as *The Depression* that shelters the *Dungeon Star*. This manual is not meant to reveal all information about the game, but is meant to guide players who are new to the genre of roguelikes, or to provide specific information to **Dungeon Star**.

# Gameplay
The current goal of **Dungeon Star** is to reach the lowest point of the dungeon with the *Dungeon Star* in hand.

Within the two-dimensional overhead view of a floor of the duneon, you are represented by **\@** (as in, the player is *at* this location). Your obstacles are the inhabitants of *The Depression*, who appear to be various creatures represented by the letters of the alphabet.

## Character Creation

At the start of any new game, you will get the chance to customize the abilities and starting equipment of your characters. The six abilities you can choose from are:

* **Strength** - determines how much damage the protagonist can deal, and the amount the player can carry in their inventory.
* **Dexterity** - determines how effective the protagonist's armor is, and how likely the protagonist is to step on a trap.
* **Constituion** - determines the amount of health the protagonist starts with, and the protagonist's natural poison resistance.
* **Intelligence** - *currently unused*.
* **Wisdom** - determines the protagonist's natural amnesia resistance.
* **Charisma** - *currently unused*.

The protagonist is also able to follow an **inspiration**, which gives them a boost to certain ability scores, and determines their starting equipment. Those inspirations are:

* **Self** - the protagonist gains their power from within themselves; no challenge is impossible, because they've made it this far without backing down. *Starts with a tower shield.*
* **Love** - the protagonist driven by an intense love, either for their loved ones, or for all life, and only wishes acquire the *Dungeon Star* to protect their love. *Starts with a wand of Pacification.*
* **Peace** - the protagonist seeks a silent future, devoid of all conflict. *Starts with a +2 dagger and a wand of Striking.*
* **Prosperity** - the protagonist seeks to fulfill all of their material desires through whatever means they deem necessary. *Starts with a wand of Greed and scrolls of Detect Items.*
* **The Arts** - the protagonist is driven by the urge to preserve and cultivate the creation of arts. *Starts with a wand of Lightning and scrolls of Enchantment.*
* **The Stars** - the protagonist is motivated by the chance to study the vastness and wonders of the sky, and will scour every face of the planet to find the right tools to do so. *Starts with a ring of Dowsing, and scrolls of Mapping and Detect Aura.* 

## Combat

To attack an enemy, attempt to walk into it. Not all enemies will be so easy to attack, so here are a few tips to deal with them:

* If you find yourself surrounded by enemies, retreat into a 1-tile wide tunnel. It will be easier to deal with one enemy at a time, instead of being assaulted on every side.
* Use items to your advantage! Many deaths can be prevented not by running-and-gunning, or racing through the dungeon as soon as possible, but by using the right item at the right time.
* Both the player and enemies can attack in all 8 directions, so if you are only using the arrow-keys to move adjacent to an enemy in the cardinal directions, they will almost certainly be able to get a hit on you.

## Hunger
The threat of starvation is a constant threat in *The Depression*. Luckily for you, a current surplus of food stuffs caused by rampant item imbalancing means that you shouldn't face any real threat of starvation. For now. To eat food items, open the inventory with **i** and select the food item you want to eat. Sometimes, monster will drop their corpses (represented by **%**), and their flesh can be extracted by pressing **x**.

As long as you aren't hungry, your health will heal automatically. There's almost no reason to rush through the dungeon.

## Identification

Many items within the *The Depression* are foreign to surface-dwellers, and as such, the protagonist will almost certainly be unable to recognize them. The types of items that appear **unidentified** include potions, scrolls, wands, and rings. Most items will be identified upon use, but this isn't universally true. As such, magics exist that can identify the protagonist's items.

The identity of each item is different every new game, so don't rely the identity of one item to be the same from a previous game (e.g. a Diet Dr. Fabulous may be a poison potion one game, but be a potion of cure poison the next game).

## *Wizard Mode*

*Wizard Mode* is a debug mode meant to access difficult portions of the game without skill. Once initiated, you cannot exit *Wizard Mode*, and high scores will not be saved.

# *The Depression*

*The Depression* is a mega-dungeon formed via unknown means. Some theorize that it's the remnants of a crater left behind after the *Dungeon Star* fell to Earth; others believe that a great mage formed the dungeon using the power of the crown. Either way, your goal is to dive into *The Depression*, retreive the *Dungeon Star*, and reach the lowest point of the dungeon. Of course, the *Dungeon Star* is functionless in the current version of the game, and the variety in enemies and items spawned stops after around 20 levels down, so the overall method of getting to the lowest point should be of little concern.

## Traps

Hidden traps can be found within the dungeon (represented by a **^**), which may slow (or halt) your progress downwards. The higher your Dexterity score is, the less likely you are to reveal or interact with a trap. The same goes for other creatures within the dungeon.

Traps can be revealed by searching (done by pressing **s**). It may take several attempts of searching in the same spot to reveal a trap.

# Items

There are several items to be found within *The Depression* to help you on your quest to finding the *Dungeon Star*.

## Potions and Scrolls

Potions (represented by **!**) are found in the dungeon as a cans of soft drink from the centuries-defunct Dr. Fabulous Corporation. When consumed, they may give some effect to the protagonist, and provide a small amount of nutrition.

Scrolls (represented by **?**) are found as mislabelled scrolls from a mad wizard who once roamed the dungeon. They enable the user to perform some magic spell when read. However, they can only be used once, so consider the best opportunity to use them!

## Wands

Wands (represented by **/**) appear in many materials in the dungeon, and, like scrolls, allow the user to perform a magic spell when used. They have a limited number of charges, so they can be used multiple times before being depleted of energy.

## Rings

Rings (represented by **=**) give the protagonist a more permanent magical effect than spells or potions, and one can be worn on both the left and right hand.

## Light Sources

Light sources can be found in the dungeon to increase the protagonist's field of view. Some items (like candles) only last for a certain amount of time, but it is rumored that some sources of light don't run out of power.

# Controls

## Menu Manipulation

* ? - list controls
* *Escape* - exit menu

## Movement

* *Up/Down/Left/Right* - cardinal movement
* 8/2/4/6 - cardinal movement
* j/k/h/l - cardinal movement
* 7/9/1/3 - diagonal movement
* u/i/b/n - diagonal movement
* . - wait turn, select entity under cursor
* 5 - wait turn, select entity under cursor
* **>** - descend stairs
* **<** - ascend stairs

## Environemt Interaction

* s - search surrounding tiles
* , - grab item
* g - grab item
* x - butcher corpse
* ; - look at entity

## Character Interaction

* i - open inventory
* d - drop item
* TAB - show character screen

## Other

* Ctrl + s - save game and exit to main menu
* Ctrl + q - quit game without saving
* Ctrl + f - toggle fullscreen
* Ctrl + w - enter *Wizard Mode*

## Debug Keys (only available from *Wizard Mode*)

* F1 - print game info to the console
* F2 - toggle FOV view
* F3 - identify all present items on level
* Ctrl + F*X* - print information to a log file instead of the console, when appropriate