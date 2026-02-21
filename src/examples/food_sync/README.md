# Exercise 0 — Sync foodtruck

Producer → ingredients → cook → prepare → Customer
---

## Task 1 — > Add Timing Information ⏱️

**Goal:** Understand where time is spent.

### What to do

Measure time spent in each stage (ingredients, cook, prepare) and
total time per order. Print the timings when an order is completed.

## Key concept

Sequential execution and latency accumulation.

## Task 2 — Process Multiple Orders 🚶🚶🚶

**Goal:** See how blocking affects throughput.

### What to do

Increase the number of orders (e.g. from 5 to 20). Add a timestamp before starting each order.

## Key concept

Throughput vs latency in a synchronous pipeline.
