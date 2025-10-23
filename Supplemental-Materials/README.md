# Supplemental Materials

This folder contains **optional** resources for deeper understanding and alternative viewpoints on systems, security and risk. They are helpful when you want more information, but **not required** to complete the course. Also, the material listed here is not complete, but should be considered a cureted list of references that you from time to time neeed to go beyond. We have tried to sort the material according to the Yacraf phases.  

We also include an example that shows how to work through the different phases. It doesn’t use Yacraf calculator tool, but it’s helpful if you get stuck or want another perspective. You can use this example to understand the intent of each phase before applying Yacraf.


## Per-phase extras

### Using UML Diagrams in Conceptual Modeling

For a quick introduction to UML in the context of conceptual modeling, we recommend the following short videos:

-  [Object diagrams](https://www.youtube.com/watch?v=OkxNKOAcOC0)
-  [Class diagram, part 1](https://www.youtube.com/watch?v=enx416yT55M)
-  [Class diagram, part 1](https://www.youtube.com/watch?v=KtCQDKZ64sY&pp=QAA%3D)

Note that UML was developed primarily for software design and code generation; in conceptual modeling, not all UML constructs are relevant, and examples drawn from software contexts can feel slightly misaligned. When watching, interpret scenarios like the “Frogger game” as stand-ins for the real-world domain you wish to model, focusing on how objects, classes, and relationships capture domain semantics rather than implementation details.

### Business Analysis - Phase 1 
**Suggested readings**
- **Business Analysis Canvas** — article/overview can be found [here] (https://www.batimes.com/articles/business-analysis-canvas-roadmap-to-effective-ba-excellence.html).
-  CATWOE looks at what a company wants to achieve, and which solutions can influence the stakeholders: intro [note](https://www.toolshero.com/problem-solving/catwoe-analysis/), and a short YouTube [video](https://www.youtube.com/watch?v=lvQYLIzE9gE) explainer *“What is CATWOE?”*.

### System Definition and Decomposition 

**Suggested readings & tools**
- **DFDs** — short primer/guide [here](https://www.lucidchart.com/pages/data-flow-diagram).
- **Diagramming tools:** [draw.io](https://www.drawio.com/), [Lucidchart](https://www.lucidchart.com/pages).  
- **Threat-modeling tools:** [Microsoft Threat Modeling Tool (legacy)](https://docs.microsoft.com/en-us/azure/security/azure-security-threat-modeling-tool), OWASP [Threat Dragon](https://www.threatdragon.com/).

**ICT component primers (pick what you need)**

It is beneficial to understand and review a number of key concepts around ICT systems and their security before you create DFDs. Various types of Information and Communication Technology (ICT) components like Database, Network, Cloud, Operating Systems, Identity and Access Management are used in an enterprise. Short introduction and link to some reading materials related to ICT components are provided in this section for interested candidates. Some standard books are also referred; if someone from non-IT background wants to go deeper in those topics, the books are available in KTH Library. 


- **Databases — what & why (5–10 min)**
  - Overview video [here](https://www.youtube.com/watch?v=Tk1t3WKK-ZY)
  - *Relational Database Concepts*: [here](https://www.youtube.com/watch?v=NvrpuBAMddw)
  - Books: 
    - *Fundamentals of Database Systems* (Elmasri/Navathe) 
    - *Database System Concepts* (Silberschatz/Korth/Sudarshan)

- **Networks — the basics (10 min)**
  - Crash Course CS #28 (Computer Networks): [here](https://www.youtube.com/watch?v=3QhU9jd03a0)
  - Book: *Computer Networking: A Top-Down Approach* (Kurose/Ross)

- **Operating Systems — orientation (10 min)**
  - “Operating Systems 1: Introduction”: [here](https://www.youtube.com/watch?v=5AjReRMoG3Y)
  - Books: 
    - *Operating System Concepts* (Silberschatz/Galvin/Gagné)
    - *Modern Operating Systems* (Tanenbaum) 

- **Identity & Access Management (IAM) — core ideas (8–12 min)**
  - Identity Management 101: [here](https://www.youtube.com/watch?v=bBH-bZbnL5Q)
  - IAM: Technical Overview: [here](https://www.youtube.com/watch?v=Tcvsefz5DmA)

- **Cloud — the big picture (6 min)**
  - “Cloud Computing in 6 Minutes” (intro video): [here](https://www.youtube.com/watch?v=M988_fsOSWo)

- **Security mechanisms — where controls live (skim)**
  - MITRE **D3FEND** (defensive techniques): [here](https://d3fend.mitre.org/)
  - Short explainers playlist: Anti-malware [here](https://www.youtube.com/watch?v=2HWediIfbvs), IDS/IPS [here](https://www.youtube.com/watch?v=hEgWPWIuq_s), Firewalls [here](https://www.youtube.com/watch?v=mDKKqPxMpb0), Logging [here](https://www.youtube.com/watch?v=uHEMxTi4YLM), Encryption [here](https://www.youtube.com/watch?v=37zZId-DNlo), Honeypots [here](https://www.youtube.com/watch?v=1PTw-uy6LA0)



### Threat Analysis 
**Suggested readings**
- **MITRE ATT&CK (Groups):** catalog of known actors and behaviors [here](https://attack.mitre.org/groups/).  
  *Note:* this is a U.S./Western perspective—use it as inspiration, not ground truth.
- **CISA / US-CERT advisories:** current threat activity and alerts [here](https://www.us-cert.gov).
- **ATT&CK intro video:** “What is MITRE ATT&CK? (basic terminology)” [here](https://www.youtube.com/watch?v=bK5eFF-HgC4&feature=emb_title).
- **Organization-specific profiling:** guide to building your own threat profiles [here](https://www.sans.org/reading-room/whitepapers/threats/creating-threat-profile-organization-35492).
- **STIX (Structured Threat Information Expression):** language for describing actors/campaigns [here](https://oasis-open.github.io/cti-documentation/stix/intro).

### Attack and Resilience Analysis 
Use this subsection to quickly deepen Phase 4: find and rate vulnerabilities, name and structure attacks (trees/graphs), and pick defenses that actually break the paths—links below are short, practical primers.

#### Security properties (start here)
- **CIA triad (Confidentiality, Integrity, Availability)** — short explainer: [here](https://www.youtube.com/watch?v=j8FT9WqmuDY)
- **AuthN vs AuthZ** — know the difference before you model controls: [here](https://www.youtube.com/watch?v=u6-sUkoAQ9w)

#### Vulnerabilities (find, rate, and reference)
- **Scanning basics** — intro to Nmap/Nessus/Nexpose: [here](https://www.youtube.com/watch?v=37zZId-DNlo)
- **Pen-testing tool** — Metasploit overview: [here](https://www.metasploit.com/)
- **Vuln catalogs** — NVD [here](https://nvd.nist.gov/) · CVE [here](https://www.cve.org/) · CWE [here](https://cwe.mitre.org/)
- **Severity scoring** — CVSS overview (FIRST): [here]( https://www.first.org/cvss/)
- **Additional references** — CERT/CC notes: [here](https://kb.cert.org/)

#### Attacks (name, structure, and reason about paths)
- **Knowledge bases** — MITRE **ATT&CK** techniques: [here](https://attack.mitre.org/matrices/enterprise/) · **CAPEC** patterns: [here](https://capec.mitre.org/)
- **Attack trees/graphs** — Schneier’s “Attack Trees”: [here](https://www.schneier.com/academic/archives/1999/12/attack_trees.html) · step-by-step guide/thesis: [here](https://essay.utwente.nl/79133/1/Sonderen_MA_EEMCS.pdf)
- **Web/app specifics** — OWASP Cheat Sheet: Web Service Security: [here](https://cheatsheetseries.owasp.org/cheatsheets/Web_Service_Security_Cheat_Sheet.html)

### Risk Assessment and Recommendations 

**Suggested readings**
- Short articles giving perspective on risk roll-up and communicating recommendations: 
    - [Article 1](https://www.forbes.com/sites/forbestechcouncil/2023/06/21/roi-for-cybersecurity-how-to-position-security-solutions-as-investments/) 
     - [Article 2](https://www.techrepublic.com/article/how-companies-determine-cybersecurity-budgets/)


## General threat-modeling references
- A paper discussing automation threat modeling using Large Language model For Banking System → [Link](https://arxiv.org/pdf/2411.17058). 
- A collection and summary of different threat modelling approaches → [Link](https://insights.sei.cmu.edu/sei_blog/2018/12/threat-modeling-12-available-methods.html)

- A Hybrid Threat Modeling Method by Carnegie Mellon University -> [Link](https://resources.sei.cmu.edu/asset_files/TechnicalNote/2018_004_001_516627.pdf) 
- Summarization of Threat Modelling Mindset → [Link](https://roberthurlbut.com/r/BSC2017TM)

- Title of books about threat modeling: 
    - Securing Systems: Applied Security Architecture and Threat Models ISBN: 978-1482233971 
    - Threat Modeling: Designing for Security ISBN: 978-1118809990

- An ebook about the method PASTA (via KTH library): Risk Centric Threat Modeling: Process for Attack Simulation and Threat Analysis →  [Link](https://learning.oreilly.com/library/view/risk-centric-threat/9780470500965/c08.xhtml#c8)
- A recorded presentation introducing the PASTA threat-modeling method → [Link](https://www.youtube.com/watch?v=TcwPZKMVZu4)

- Notes on Yacraf relation to PASTA → [Link](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/blob/master/Supplemental-Materials/Notes_on_Yacraf_relation_to_PASTA.md)

- An ebook about the method FAIR (via KTH library): Measuring and Managing Information Risk: A FAIR Approach → [Link](https://learning.oreilly.com/library/view/measuring-and-managing/9780124202313/XHTML/contents.xhtml)

- FAIR overview ppt -> [Link](https://cdn2.hubspot.net/hubfs/1616664/The%20FAIR%20Model_FINAL_Web%20Only.pdf)

- Notes on Yacraf relation to FAIR → [Link](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/blob/master/Supplemental-Materials/Notes_on_Yacraf_relation_to_FAIR.md)
