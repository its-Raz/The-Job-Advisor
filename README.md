<h1 align='center' style="text-align:center; font-weight:bold; font-size:2.5em"> The Job Advisor<br>Final Project Lab Data Collection </h1>

<p align='center' style="text-align:center;font-size:1em;">
    <a>Amit Zalle</a>&nbsp;,&nbsp;
    <a>Shalev Hermon</a>&nbsp;,&nbsp;
    <a>Raz Biton</a>&nbsp;,&nbsp;
    
    <br/> 
    Technion<br/> 
    
</p>

[[Project Report](https://arxiv.org/abs/2307.10490)]



# Contents

- [Overview](#overview)
- [JobScraping](#JobScraping)
- [Experiments](#experiments)
  - [Injection Attacks in LLaVA](#injection-attacks-in-llava) :volcano:
    - [Image Perturbation](#image-perturbation-llava)
  - [Injection Attacks in PandaGPT](#injection-attacks-in-pandagpt) :panda_face:
    - [Image Perturbation](#image-perturbation-pandagpt)
    - [Sound Perturbation](#sound-perturbation)
- [Other Examples](#other-examples)
- [Citation](#citation)

# Overview

**Job Advisor Overiew**

Some Text.

|                                                  Image Example                                                  |                    Sound Example                     |
| :-------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------: |
| <img src="./result_images/llava-potter.png" width=45%> <img src="./result_images/llava-pirate.png" width=48.6%> | <img src="./result_images/panda-audio-phishing.png"> |

# JobScraping

In order to scrape job you will need to have accsess to bright data Web Browser 

1. Clone this repository and navigate to multimodal injection folder

   ```bash
   git clone https://github.com/ebagdasa/multimodal_injection.git
   cd multimodal_injection
   ```

2. Create conda environment for LLaVA

   ```bash
   cd llava
   conda create -n llava_injection python=3.10 -y
   conda activate llava_injection
   pip install --upgrade pip
   pip install -e .
   ```

3. Create conda environment for PandaGPT

   ```bash
   cd pandagpt
   conda create -n pandagpt_injection python=3.10 -y
   conda activate pandagpt_injection
   pip install -r requirements.txt
   ```

4. Download model checkpoints for LLaVA

   Please refer to this [link](https://github.com/haotian-liu/LLaVA/tree/main#llava-weights) from [LLaVA](https://github.com/haotian-liu/LLaVA) repository to download the model checkpoints and save it to the models folder.

   We use LLaVA-7B weights in our experiments.

5. Download model checkpoints for PandaGPT

   Please refer to this [link](https://github.com/yxuansu/PandaGPT#2-running-pandagpt-demo-back-to-top) from [PandaGPT](https://github.com/yxuansu/PandaGPT) repository to download all the model checkpoints (ImageBind, Vicuna, PandaGPT) and save them to the models folder.

   We use pandagpt_7b_max_len_1024 weight in our experiments.
