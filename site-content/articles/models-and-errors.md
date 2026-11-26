---
title: 物理模型中的近似与误差
slug: models-and-errors
date: 2026-11-26
category: physics
category_label: 物理 · 方法笔记
excerpt: 一个模型何时有效，往往取决于未被写出来的假设。
keywords: 物理, 近似, 误差
draft: false
sample: true
---

> **排版示例**：以下为文章格式示范，不代表作者已完成的科研项目。

## 近似意味着什么

在满足小角度条件时，有 $\sin\theta\approx\theta$。这个近似不是恒等式，它依赖 $\theta$ 接近零的假设。

$$
\sin\theta = \theta-\frac{\theta^3}{3!}+\frac{\theta^5}{5!}-\cdots
$$

## 误差与有效范围

对于足够小的角度，三阶项给出下一阶误差的量级。因此需要说明模型在哪个范围内可用，而不是只展示一个简洁的式子。

## 写在笔记最后

任何模型都应标明边界条件、所用单位和关键近似，并保存用于交叉检查的原始资料。
