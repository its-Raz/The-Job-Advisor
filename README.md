<h1 align='center' style="text-align:center; font-weight:bold; font-size:2.5em"> The Job Advisor<br>Final Project Lab Data Collection </h1>

<p align='center' style="text-align:center;font-size:1em;">
    <a>Amit Zalle</a>&nbsp;,&nbsp;
    <a>Shalev Hermon</a>&nbsp;,&nbsp;
    <a>Raz Biton</a>&nbsp;,&nbsp;
    
    <br/>Technion<br/> 
    
</p>

[[Project Report](https://arxiv.org/abs/2307.10490)]



# Contents

- [Overview](#overview)
- [JobScraping](#JobScraping)
- [Other Examples](#other-examples)
- [Citation](#citation)

# Overview

**Job Advisor Overiew**

1. Clone this repository and 

   ```bash
   git clone https://github.com/ebagdasa/multimodal_injection.git
   cd multimodal_injection
   ```
2. Create env

   ```bash
   git clone https://github.com/ebagdasa/multimodal_injection.git
   cd multimodal_injection
   ```   



# JobScraping

In order to scrape job you will need to have accsess to bright data Web Browser

1. Enter `JobScraper` folder then `main.py`, at the top of the file, below all imports please add your Bright Data log in details:
    ```username='ENTER USERNAME'
       password='ENTER PASSWORD'
       auth=f'{username}:{password}'
       host = 'brd.superproxy.io:9222'
       browser_url = f'wss://{auth}@{host}'
   ```
|                    Image Example                        | 
| :------------------------------------------------------ | 
| <img src="./images/login.JPG" width=45%>  |
2. 


