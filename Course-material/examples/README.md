## Examples

...soon to appear. 

## About the Business Architecture Modelling
The cloud example that we provide does not include business architecture modelling (Phase 2). If you are struggling with this part and feel that you need an example, we advise you to look at the [legacy_example](https://github.com/KTH-SSAS/EP2791-Cybersecurity-Threat-Modeling-and-Risk-Analysis/tree/master/Supplemental-Materials/examples_legacy) provided in the supplementary material.

For reminder, the goal of Phase 2 is to build a clear understanding of the company’s business purpose and how value is delivered. This phase is used to:

1. Identify the company’s main business goals.

2. Describe the business architecture through concrete use cases (who does what, using which systems).

3. Anticipate where failures in these activities could create real business impact later in the analysis.

In the legacy example, we consider a e-scooter company. The company’s primary business goal is “rent out more scooters than any other company in Stockholm.” To support this, the company defines several operational objectives:

- Collect and utilize ride data to improve scooter quality and the customer experience. This involves the scooters themselves, the backend systems, and analytics platforms that process usage data.

- Keep customer satisfaction above 90%. This is done by running satisfaction surveys directly in the customer mobile app and acting on that feedback.

- Maintain scooter uptime above 98%. In practice, this means having teams in the field who relocate scooters, charge low-battery scooters, collect damaged scooters, and decide whether each scooter should be repaired or removed from the fleet.

The business architecture is then described through the main use cases that realize those objectives. For example:

- “Customer renting a scooter” links the customer, the mobile rental app, the backend rental server, and the physical scooter.

- “Charging / relocating scooters” links the scooter charging/relocation team with their operational tools (relocation client/server) and the scooters in the field.

- “Scooter repair / removal” links the maintenance workers and repair admins with the repair systems (repair client/server) to decide if a scooter is fixed and returned to service or permanently removed.

Capturing these use cases is important because they show how actors (customers, BI analysts, relocation teams, repair teams) interact with assets (apps, servers, analytics cloud, physical scooters) to achieve the business goals. Later, in the risk assessment, we will look at what happens if any of these critical interactions fails, for example, if rentals cannot be initiated, if damaged scooters are not collected, or if satisfaction feedback cannot be gathered.
