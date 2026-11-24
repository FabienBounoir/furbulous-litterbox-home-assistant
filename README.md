<div align="center">

<img src="custom_components/furbulous/icon.png" width="96" alt="Furbulous">

# Furbulous Cat for Home Assistant

**Real-time integration for the Furbulous self-cleaning litter box: cat presence, weight, visits, alerts and controls, in Home Assistant and Apple Home.**

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Release](https://img.shields.io/github/v/release/FabienBounoir/furbulous-litterbox-home-assistant)](https://github.com/FabienBounoir/furbulous-litterbox-home-assistant/releases)
![IoT class](https://img.shields.io/badge/IoT-cloud__push-brightgreen)
![HomeKit](https://img.shields.io/badge/HomeKit-ready-black?logo=apple)
![Languages](https://img.shields.io/badge/i18n-EN%20·%20FR%20·%20DE%20·%20ES%20·%20IT-blue)

[![Add repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FabienBounoir&repository=furbulous-litterbox-home-assistant&category=integration)

</div>

![Dashboard](docs/images/dashboard.jpg)

---

## ✨ Highlights

- ⚡ **Real time, not polling.** Uses the same WebSocket push channel as the official app: the cat is detected about 1 s after stepping in, with far less data than polling every 30 s.
- 🐈 **Knows the difference** between a cat *in front of* the box, a cat *inside*, and a cleaning cycle.
- 🎯 **Automation events** (`furbulous_event`): cat nearby, cat entered, cat left with visit duration and weight, cleaning done.
- 🔔 **Official alerts** (waste bin full, lid not installed…) as a sensor and as a `furbulous_notification` event.
- 📱 **Plays nice with the phone app.** The account allows a single session: when you open the app, the integration steps aside for 5 minutes, then reconnects by itself.
- 🌍 **All regions** (Europe, Americas, Asia-Pacific, China) and **5 languages**.
- 🍎 **HomeKit-friendly** entity types (occupancy, motion, switches).
- 🩺 **Diagnostics** download with credentials redacted, for bug reports.

---

## 📦 Installation

### HACS (recommended)

1. Click the **Add repository to HACS** button above, or add `https://github.com/FabienBounoir/furbulous-litterbox-home-assistant` as a custom repository (category **Integration**).
2. Download **Furbulous Cat** and restart Home Assistant.

### Manual

Copy `custom_components/furbulous` into your `config/custom_components/` folder and restart Home Assistant.

### Configuration

**Settings → Devices & services → Add integration → Furbulous Cat**, then sign in with your Furbulous app account and pick the server region your app uses.

<img src="docs/images/config-flow.jpg" width="420" alt="Configuration">

> [!IMPORTANT]
> Furbulous accounts allow **one session at a time**. Logging into the phone app signs Home Assistant out (and vice versa). The integration handles this: it waits **5 minutes** so you can use the app, then logs back in. Entities keep their last value in the meantime.

---

## 🧭 How it works

```mermaid
flowchart LR
    box["🐈 Litter box"] -- IoT link --> cloud["☁️ Furbulous cloud<br/>(AWS)"]
    cloud -- "WebSocket push<br/>(real time)" --> ha["🏠 Home Assistant<br/>furbulous integration"]
    ha -- "REST every 15 min<br/>(daily stats, alerts, firmware)" --> cloud
    ha -- "REST commands<br/>(clean, modes…)" --> cloud
    ha --> lovelace["📊 Dashboards"]
    ha --> automations["⚙️ Automations<br/>furbulous_event"]
    ha -- HomeKit Bridge --> apple["🍎 Apple Home / Siri"]
```

Every property change (presence, weight, cleaning state, errors) arrives instantly over the WebSocket. REST is only used for commands, daily statistics, alerts and firmware info, and as a safety net.

### Single-session handling

```mermaid
sequenceDiagram
    participant HA as Home Assistant
    participant Cloud as Furbulous cloud
    participant Phone as Phone app
    HA->>Cloud: logged in, WebSocket connected
    Phone->>Cloud: you open the app (login)
    Cloud-->>HA: token invalid (10403)
    Note over HA: steps aside, no re-login for 5 min<br/>(entities keep last values)
    Phone->>Cloud: you change settings…
    HA->>Cloud: after 5 min: login + refresh
    Cloud-->>Phone: phone app signed out
```

### Litter box states

```mermaid
stateDiagram-v2
    direction LR
    Idle: 0 · Idle
    Nearby: 5 · Cat in front
    Inside: 6 · Cat inside
    Cleaning: 1 · Cleaning
    Idle --> Nearby: cat approaches
    Nearby --> Inside: steps in (cat_entered)
    Inside --> Idle: leaves (cat_left)
    Idle --> Cleaning: auto / manual clean
    Cleaning --> Idle: done (cleaning_done)
```

---

## 🧩 Entities

<img src="docs/images/device.jpg" width="560" alt="Device page">

| Type | Entity | Notes |
|---|---|---|
| Binary sensor | **Cat in litter box** | `occupancy`, real time (`workstatus` 6) |
| Binary sensor | **Cat in front of litter box** | `motion`, entrance presence sensor (`workstatus` 5) |
| Binary sensor | Waste bin full · Connected · Child lock · Sleep mode | |
| Sensor | **Last activity** | Time of the last visit, with `duration_seconds` and `cat_weight` attributes |
| Sensor | Cat weight · Daily uses · Average daily duration · Error | Daily stats refresh as soon as the cat leaves |
| Sensor | **Last notification** | Text of the latest app alert, plus the 5 most recent in `recent` |
| Button | Manual clean · Pause · Resume · Empty litter · Pack waste | |
| Switch | Full auto mode · Do not disturb · Child lock | |
| Select | Cleaning delay | |
| Update | **Firmware** | MCU and Wi-Fi versions (read-only: install updates from the app) |

Entity names are translated (EN, FR, DE, ES, IT) and follow your Home Assistant language.

---

## ⚙️ Automations

### Events

| Event | `type` / data | When |
|---|---|---|
| `furbulous_event` | `cat_nearby` | A cat is in front of the box |
| `furbulous_event` | `cat_entered` | The cat steps in |
| `furbulous_event` | `cat_left` + `duration` (s), `weight` (g), `end` | The cat leaves |
| `furbulous_event` | `cleaning_done` | A cleaning cycle finished |
| `furbulous_notification` | `title`, `summary`, `time` | New alert in the app (bin full, lid…) |

All events also carry `iotid` and `device_name`.

### Examples

```yaml
# Long visit: possible health issue
- alias: "Litter box: long visit"
  triggers:
    - trigger: event
      event_type: furbulous_event
      event_data: { type: cat_left }
  conditions:
    - "{{ (trigger.event.data.duration or 0) > 300 }}"
  actions:
    - action: notify.notify
      data:
        message: >
          Visit of {{ trigger.event.data.duration // 60 }} min
          ({{ trigger.event.data.weight }} g)

# Forward the app's own alerts
- alias: "Litter box: app alerts"
  triggers:
    - trigger: event
      event_type: furbulous_notification
  actions:
    - action: notify.notify
      data:
        title: "{{ trigger.event.data.title }}"
        message: "{{ trigger.event.data.summary }}"

# Night light when the cat walks up to the box
- alias: "Litter box: night light"
  triggers:
    - trigger: state
      entity_id: binary_sensor.furbulous_box_cat_in_front_of_litter_box
      to: "on"
  conditions:
    - condition: sun
      after: sunset
  actions:
    - action: light.turn_on
      target: { entity_id: light.hallway }
      data: { brightness_pct: 10 }
```

---

## 📊 Dashboard

<img src="docs/images/history.jpg" width="300" align="right" alt="History">

The screenshots come from a dashboard built with [Mushroom](https://github.com/piitaya/lovelace-mushroom), [Bubble Card](https://github.com/Clooos/Bubble-Card) and [mini-graph-card](https://github.com/kalkih/mini-graph-card). Things worth showing:

- a **status card** driven by the `work_status_code` attribute of *Cat in litter box* (0 idle, 1 cleaning, 5 in front, 6 inside);
- **last visit** from *Last activity*, with its `duration_seconds` attribute;
- a **weight trend** (30 days) and **daily uses** as bars (`group_by: date`);
- a **presence timeline** (history graph of *in* and *in front*).

<br clear="right">

---

## 🍎 HomeKit

Expose the entities through the built-in **HomeKit Bridge**:

| Entity | Apple Home accessory |
|---|---|
| Cat in litter box | Occupancy sensor, real time, usable in Home automations |
| Cat in front of litter box | Motion sensor |
| Waste bin full | Occupancy sensor by default. **Tip:** set *Show as → Opening* in the entity settings to get a contact sensor and native Apple Home notifications ("open" = full) |
| Buttons and switches | Switches (buttons turn themselves off) |

Apple Home has no generic numeric or text sensor, so weight, statistics, errors and notifications stay in Home Assistant. Consider excluding **Empty litter** and **Pack waste** from HomeKit: Home has no confirmation step.

---

## 🔍 Decoded values

| `workstatus` | Meaning |
|---|---|
| 0 | Idle |
| 1 | Cleaning |
| 5 | Cat in front of the box |
| 6 | Cat inside |

| `errorReportEvent` | Meaning |
|---|---|
| 0 | No error |
| 16 | Litter full |
| 64 | Drawer not in place |
| 128 | Cover open |
| 4096 | Cat nearby (informational, not an error) |

Found another value? Download the diagnostics (**Settings → Devices → Furbulous Box → ⋮ → Download diagnostics**). Credentials are redacted. Open an issue with the file and what the box was doing.

---

## 🛠️ Development

```bash
python tests/test_kick.py   # session handling + value normalization (needs `requests`)
```

API notes from reverse engineering the Android app live in [`docs/`](docs). PRs welcome!

## 📄 License

MIT. See [LICENSE](LICENSE). Not affiliated with Furbulous.
