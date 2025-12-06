# Requirements Document

## Introduction

This document specifies the requirements for fixing three issues in the Multi-Agent Swarm application:
1. Unknown role errors when the Architect tries to spawn agents using display names instead of role keys
2. User input in chat should display the username with a distinct color for differentiation
3. The dashboard should be the default entry point when running the Python application

## Glossary

- **Swarm**: The collection of AI agents working together in the chatroom
- **Architect**: The lead agent (Bossy McArchitect) that orchestrates other agents
- **Role Key**: The internal identifier for an agent type (e.g., "backend_dev")
- **Display Name**: The human-readable name of an agent (e.g., "Codey McBackend")
- **Dashboard**: The Rich-based terminal UI that provides a visual interface for the swarm
- **spawn_worker**: A tool that creates new agent instances dynamically

## Requirements

### Requirement 1

**User Story:** As the Architect agent, I want to spawn workers using either role keys or display names, so that I can naturally refer to team members by their names.

#### Acceptance Criteria

1. WHEN the Architect calls spawn_worker with a display name (e.g., "Codey McBackend") THEN the system SHALL map it to the correct role key and spawn the agent
2. WHEN the Architect calls spawn_worker with a role key (e.g., "backend_dev") THEN the system SHALL spawn the agent as before
3. WHEN the Architect calls spawn_worker with an unrecognized name THEN the system SHALL return an error message listing valid role keys and display names
4. WHEN a new agent is spawned THEN the system SHALL announce the agent joining with their display name

### Requirement 2

**User Story:** As a user chatting in the swarm, I want my messages to display my username with a distinct color, so that I can easily differentiate my input from agent responses.

#### Acceptance Criteria

1. WHEN a user sends a message THEN the system SHALL display the username with a distinct color (lime green) before the message content
2. WHEN displaying user messages THEN the system SHALL use the same timestamp format as agent messages
3. WHEN the user changes their username via /name command THEN the system SHALL use the new name with the same distinct color

### Requirement 3

**User Story:** As a user, I want the dashboard to be the default interface when running the application, so that I can use the rich visual UI for interacting with the swarm.

#### Acceptance Criteria

1. WHEN the user runs `python main.py` THEN the system SHALL launch the dashboard interface by default
2. WHEN the dashboard launches THEN the system SHALL prompt for project selection before starting
3. WHEN the dashboard is running THEN the system SHALL display agent status, tasks, and chat in a structured layout
4. WHEN the user sends a message in the dashboard THEN the system SHALL display it with the username and distinct color

### Requirement 4

**User Story:** As a user, I want to see token usage statistics in the dashboard, so that I can monitor API consumption and costs.

#### Acceptance Criteria

1. WHEN the dashboard is running THEN the system SHALL display a token counter panel showing cumulative token usage
2. WHEN an agent makes an API call THEN the system SHALL update the token counter with prompt tokens and completion tokens
3. WHEN displaying token usage THEN the system SHALL show total tokens used in the current session
4. WHEN the session ends THEN the system SHALL display a summary of total tokens consumed

### Requirement 5

**User Story:** As a user, I want the dashboard settings menu to provide comprehensive control over the swarm, so that I can manage all aspects from one place.

#### Acceptance Criteria

1. WHEN the user opens the settings menu THEN the system SHALL display options for: username, bot management, model selection, tools toggle, delays, and project management
2. WHEN the user selects bot management THEN the system SHALL allow enabling/disabling individual agents
3. WHEN the user selects model selection THEN the system SHALL allow changing the model for each agent
4. WHEN the user selects project management THEN the system SHALL allow switching projects or creating new ones
5. WHEN the user changes a setting THEN the system SHALL persist the change and apply it immediately
