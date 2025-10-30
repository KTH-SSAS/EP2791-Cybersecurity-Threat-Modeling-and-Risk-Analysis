# Main Course Material

The main study material for this course is the [Yet another cybersecurity risk assessment framework (Yacraf)](https://link.springer.com/article/10.1007/s10207-023-00713-y). To complement this paper, this directory contains the key material for the course, organized into two main subdirectories:

- [**Lectures**](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/blob/master/Course-material/lectures); that contains the lecture slides and recorded videos, organized by Yacraf phases (0–5). 

- [**Example**](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/tree/master/Course-material/examples); as an inspiration to get started in using the Yacraf tool a small example centered around three abuse cases is provided.  


# Complementary Tools (Beyond the Yacraf calcualtion tool)

Yacraf is organized in phases, but **the Yacraf tool is not intended for all of them**. The Yacraf tool supports the risk calcualtions defined in the framework, however it is not supporting the modeling of business and IT-systems architectue. For this, other tools are better. 

## Threat modeling languages

Even though Yacraf does not mandate any specific language for describing business and IT-systems architectiures it does suggest a taxonomy that support the architecture modeling as is explained in [Phases 1 and 2 in the material](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/edit/master/Course-material/lectures). From a Yacraf point of view, the important thing is that the architectural modeling supports the development of *Loss Events, Abuse Cases*, etc., that drives the risk calculations. Some examples of architecture models can be found under the [supplementary material](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/tree/master/Supplemental-Materials/examples_legacy).  

Traditional threat modeling primarily uses Data Flow Diagrams (DFDs), extended with trust boundaries, to describe the system architecture. [Learn more about DFDs here.](https://online.visual-paradigm.com/knowledge/software-design/dfd-using-yourdon-and-demarco/)

## Recommended Tools
A general recommendation would be to use [**draw.io**](https://draw.io) for the architecture modeling in this course. This is a very flexible general diagramming and data modeling tool that allows you to do model with very few imposed restrictions.

Other tools of interest are for instance: 
- [**Lucidchart**](https://www.lucidchart.com) – user-friendly diagramming platform (similar to Visio).  
- [**Microsoft Threat Modeling Tool**](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) *(no longer actively maintained)*.  
- [**Threat Dragon**](https://owasp.org/www-project-threat-dragon/) – open-source tool for threat modeling.  
