# Project Sentinel: Automated Near-Earth Object (NEO) Triage

**Domain:** Aerospace / Planetary Defense  
**Goal:** Streamline planetary-defense analyst workflows by automating the pre-triage of close-approach asteroids.

---

## 🚀 Project Overview
Project Sentinel addresses the challenge of managing the massive flow of near-Earth object tracking data. Instead of manually reviewing every object, our automated pipeline flags high-priority candidates—those that combine significant size with potentially hazardous close-approach distances—allowing analysts to focus on high-impact events.

## 🛠 Resource Audit
| Category | Specification |
| :--- | :--- |
| **API Access** | NASA NeoWs API (via personal key for high-throughput). |
| **Data pipeline** | Multi-step chaining of adjacent 7-day API windows. |
| **Log Reconciliation** | Integration with simulated ground-station logs (`ground_station_log.csv`). |
| **Supplementary Data** | Web-scraped planetary defense mission statistics. |

## 🎯 Classification Logic (The Triage Rule)
We implement an independent triage classifier to flag objects for human review. 
An object is flagged (`priority_watch = 1`) if:
* **Size:** `max_estimated_diameter_km >= 0.14` (Survey completeness benchmark).
* **Proximity:** `miss_distance_lunar <= 10` (Standard "close-approach" indicator).

> **Why this rule?** This acts as an independent pre-triage layer, ensuring we filter for objects that pose a high information-value risk, distinct from the standardized NASA `is_potentially_hazardous` flag.

## 📊 Key Features
Our feature engineering pipeline extracts and calculates:
* **Orbital Dynamics:** `miss_distance_lunar`, `relative_velocity_kph`.
* **Physical Metrics:** `absolute_magnitude_h`, `estimated_diameter_max/min_km`.
* **Contextual Data:** `confidence_score` (reconciled from ground logs), `approach_category`.

## 📈 ROI Metric
The success of this system is quantified by the reduction in manual triage volume:
`Workload Reduction (%) = (1 - (n_flagged / n_total)) * 100`

*We aim to demonstrate a quantifiable cut in weekly manual review time through this automated triage layer.*

---
*Developed as part of the Digital Pioneers of Egypt (DEPI) Data Science track.*