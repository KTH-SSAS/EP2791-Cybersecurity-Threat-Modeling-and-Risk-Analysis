## Examples

The example is presenting a threat model with YACRAF-tool. It is based on [this cloud infrastructure example](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/blob/master/Course-material/examples/Cloud_example_infrustructure.png), as an inspiration to create [this YACRAF-tool model](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/tree/master/YACRAF-Calculator-Tool/saves/Cloud). The YACRAF-tool model contains two attackers, three associated abuse cases and three loss events. Each abuse case has a related tab with an attack tree and defense mechanisms. We provide two simplified attack trees and one more complex one, with two paths described in detail. This material is explained in a number of videos:

1. Infrustructure description → [video 1 ▶](https://play.kth.se/playlist/dedicated/0_yxqycc9v/0_n8o3qpzp)

This video explains the cloud infrastructure scheme, focusing on internal components and data flows.

2. Explanation of Attackers, Abuse cases and Loss events → [video 2 ▶](https://play.kth.se/playlist/dedicated/0_yxqycc9v/0_aukm919d)

This video describes two types of attackers, associated abuse cases and loss events. The video explains the connection between these entities.

3. Explanation of a Theft of GCP credentials compromise abuse case → [video 3 ▶](https://play.kth.se/playlist/dedicated/0_yxqycc9v/0_0tsn1yu7)

This video goes through one path of the attack tree for the Theft of GCP credentials abuse case, explaining the difference between AND and OR events and how difficulty scores are set.

4. Explanation the Theft of GCP credentials abuse case and its relation to the infrastructure → [video 4 ▶](https://play.kth.se/playlist/dedicated/0_yxqycc9v/0_wk1207ev)

This video explains how the attack path is related to the infrastructure scheme. The video follows one path for the attack tree related to the Theft of GCP credentials abuse case — compromising IAM services. The attack path is explained from the perspective of infrastructure modules.

5. Explanation for a Log deletion abuse case and its relation to the infrastructure → [video 5 ▶](https://play.kth.se/playlist/dedicated/0_yxqycc9v/0_ak24jq0k)

This video explains the attack tree associated with Log deletion abuse cases in relation to the infrastructure scheme. The video describes the relation between MITRE ATT&CK techniques and attack path nodes, and explains the insider attacker’s intentions.

6. Explanation of defense mechanisms → [video 6 ▶](https://play.kth.se/playlist/dedicated/0_yxqycc9v/0_ach0pio6)

This video explains the defense mechanisms, how to connect defense mechanisms to the attack tree and how defense mechanisms affect the difficulty scores of attack path nodes.

To open the YACRAF-tool model of this example please follow the steps:

Step 1: Make sure you have installed YACRAF-tool from [here](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/tree/master/YACRAF-Calculator-Tool).

Step 2: Navigate to the tool root directory.

Step 3: Run the command 
```
python3 main.py Cloud
```
This [article](https://www.nccgroup.com/research-blog/threat-modelling-cloud-platform-services-by-example-google-cloud-storage/) provides another inteprretation of the threat modelling for the same cloud infrastructure. It uses STRIDE model and identifies different set of attackers, assets and threats. Please note, that our YACRAF example provides different variation of the threat model, however the article still can be considered as a source of inspiration.

## About the Business Architecture Modelling
The cloud example that we provide does not include business architecture modelling (Phase 2). If you are struggling with this part and feel that you need an example, we advise you to look at the [legacy_example](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/tree/master/Supplemental-Materials/examples_legacy) provided in the supplementary material.

For reminder, the goal of Phase 2 is to build a clear understanding of the company’s business purpose and how value is delivered. This phase is used to:

1. Identify the company’s main business goals.

2. Describe the business architecture through concrete use cases (who does what, using which systems).

3. Anticipate where failures in these activities could create real business impact later in the analysis.

In the legacy example, we consider an e-scooter company. The company’s primary business goal is “rent out more scooters than any other company in Stockholm.” To support this, the company defines several operational objectives:

- Collect and utilize ride data to improve scooter quality and the customer experience. This involves the scooters themselves, the backend systems, and analytics platforms that process usage data.

- Keep customer satisfaction above 90%. This is done by running satisfaction surveys directly in the customer mobile app and acting on that feedback.

- Maintain scooter uptime above 98%. In practice, this means having teams in the field who relocate scooters, charge low-battery scooters, collect damaged scooters, and decide whether each scooter should be repaired or removed from the fleet.

The business architecture is then described through the main use cases that realize those objectives. For example:

- “Customer renting a scooter” links the customer, the mobile rental app, the backend rental server, and the physical scooter.

- “Charging / relocating scooters” links the scooter charging/relocation team with their operational tools (relocation client/server) and the scooters in the field.

- “Scooter repair / removal” links the maintenance workers and repair admins with the repair systems (repair client/server) to decide if a scooter is fixed and returned to service or permanently removed.

Capturing these use cases is important because they show how actors (customers, BI analysts, relocation teams, repair teams) interact with assets (apps, servers, analytics cloud, physical scooters) to achieve the business goals. Later, in the risk assessment, we will look at what happens if any of these critical interactions fails, for example, if rentals cannot be initiated, if damaged scooters are not collected, or if satisfaction feedback cannot be gathered.
