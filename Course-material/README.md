# Course Material

This directory contains the official materials for EP2791, organized into two subdirectories:

- **Lectures**: EP2791 lecture slides and videos, organized by Yacraf phases (0–5). View in order: Lecture 0 (Preliminaries), then 1) Business Analysis, 2) System Definition & Decomposition, 3) Threat Analysis, 4) Attack & Resilience Analysis, 5) Risk Assessment & Recommendations. Filenames match the lecture titles, a consolidated slide deck is available as [EP2790-HT2024_v1-all.pdf](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/blob/master/Course-material/lectures/EP2790-HT2024_v1-all.pdf).

- **Worked examples** 


# Complementary Tools (Beyond Yacraf)

The course is structures the Yacraf in phases, and **the Yacraf tool is not intended for all of them**. The Yacraf tool supports the risk calcualtions defined in the framework, however it is not supporting the modeling of business and IT-systems architectue. For this, other tools are better. 

## Threat modeling meta models

Even though Yacraf does not mandate any specific language for describing business and IT-systems architectiures it does suggest a taxonomy that support the architecture modeling as is explained in (Phases 1 and 2 in the material)[https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/edit/master/Course-material/lectures/README.md]. From a Yacraf point of view, the important thing is that the architectural modeling supports the development of *Loss Events, Abuse Cases*, etc. that drives the risk calculations.  

Traditional threat modeling primarily uses Data Flow Diagrams (DFDs), extended with trust boundaries, to describe the system architecture. [Learn more about DFDs here.](https://online.visual-paradigm.com/knowledge/software-design/dfd-using-yourdon-and-demarco/)

## Recommended Tools
A general recommendation would be to use [**draw.io**](https://draw.io) for the threat modelling in this course. This is a very flexible general diagramming and data modeling tool that allows you to do model with very few imposed restrictions.

Other tools of interest are for instance: 
- [**Lucidchart**](https://www.lucidchart.com) – user-friendly diagramming platform (similar to Visio).  
- [**Microsoft Threat Modeling Tool**](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) *(no longer actively maintained)*.  
- [**Threat Dragon**](https://owasp.org/www-project-threat-dragon/) – open-source tool for threat modeling.  
