\# Blender Automation MCP — Architecture Specification V1



Project: Blender-Automation-MCP  

Architecture Version: 1.0  

Status: Draft for implementation  

Validated Baseline: BLMCP-BASELINE-1  

Development Branch: architecture/capability-platform  



\## 1. Project Vision



Blender-Automation-MCP is an independent professional automation platform that allows ChatGPT and other MCP-compatible AI clients to inspect, create, modify, validate, render, animate, simulate, import, and export Blender projects.



The platform must not become a flat collection of hundreds of unrelated MCP tools.



It will use a layered architecture:



```text

ChatGPT or MCP Client

&#x20;       ↓

Public MCP Tools

&#x20;       ↓

Capability Router

&#x20;       ↓

Internal Blender Capabilities

&#x20;       ↓

High-Level Workflows

&#x20;       ↓

Blender Python API

