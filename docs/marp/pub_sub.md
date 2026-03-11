---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9

---
# Publisher Subcriber Pattern  
- Decoupled Event Communication
    - Publishers send messages  
    - Subscribers receive messages  

They **do not know about each other**.

---

## Properties

- Many-to-many communication
- Temporal decoupling (publisher doesn’t wait)
- Spatial decoupling (no direct references)
- Dynamic subscription

---

## Conceptual Flow

Publisher → Topic → Subscribers

Messages are routed based on a **topic** or **channel**.

---

# 2️⃣ Pub/Sub vs Work Queue

## Work Queue (Task Distribution)

- One message  
- Exactly one worker processes it  
- Load balancing