# Implementation Plan

- [x] 1. Fix Role Mapping for Agent Spawning





  - [x] 1.1 Add display name to role key mapping in agents/__init__.py


    - Add DISPLAY_NAME_TO_ROLE dictionary mapping lowercase display names to role keys
    - Add resolve_role() function that accepts either display name or role key
    - Update create_agent() to use resolve_role() for input normalization
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.2 Write property test for role resolution



    - **Property 1: Role Resolution Consistency**
    - **Property 2: Role Resolution Backwards Compatibility**


    - **Validates: Requirements 1.1, 1.2**
  - [x] 1.3 Update spawn_worker in agent_tools.py to use resolve_role





    - Import resolve_role from agents module
    - Wrap role lookup in try/except to provide helpful error messages
    - _Requirements: 1.1, 1.3_





- [x] 2. Implement Token Tracking



  - [x] 2.1 Create core/token_tracker.py module

    - Implement TokenTracker singleton class
    - Add add_usage(prompt, completion) method
    - Add get_stats() method returning dict with all counters
    - Add reset() method for new sessions
    - Add get_token_tracker() factory function
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 2.2 Write property test for token accumulation

    - **Property 4: Token Counter Accumulation**
    - **Validates: Requirements 4.2, 4.3**
  - [x] 2.3 Integrate token tracking into BaseAgent


    - Import token tracker in agents/base_agent.py
    - After each API call, extract token usage from response
    - Call tracker.add_usage() with prompt and completion tokens
    - _Requirements: 4.2_

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 4. Enhance Dashboard with Token Counter and User Coloring




  - [x] 4.1 Add token counter panel to dashboard layout


    - Import get_token_tracker in dashboard.py
    - Create create_tokens_panel() method
    - Add tokens panel to sidebar layout
    - _Requirements: 4.1, 4.3_
  - [x] 4.2 Add user message coloring in dashboard


    - Define USER_STYLE = "bold bright_green" for lime green
    - Update create_chat_panel() to use USER_STYLE for user messages
    - Check message.role == MessageRole.HUMAN to identify user messages
    - _Requirements: 2.1, 3.4_
  - [x] 4.3 Write property test for user message coloring


    - **Property 3: User Message Color Consistency**
    - **Validates: Requirements 2.1, 3.4**


- [x] 5. Add Project Selection to Dashboard




  - [x] 5.1 Add project selection at dashboard startup


    - Import get_project_manager in dashboard.py
    - Create select_project() method similar to main.py
    - Call select_project() before initializing chatroom
    - _Requirements: 3.2_
  - [x] 5.2 Add project management to settings menu


    - Add option to switch projects in show_settings_menu()
    - Add option to create new project
    - Show current project info
    - _Requirements: 5.4_


- [x] 6. Enhance Settings Menu




  - [x] 6.1 Add comprehensive settings options


    - Add bot management (enable/disable agents)
    - Add model selection per agent
    - Add tools toggle
    - Add delay settings (round delay, response delay)
    - Add username change
    - _Requirements: 5.1, 5.2, 5.3_


  - [x] 6.2 Write property test for settings persistence








    - **Property 5: Settings Persistence Round-Trip**
    - **Validates: Requirements 5.5**
  - [ ] 6.3 Write property test for agent state toggle
    - **Property 6: Agent State Toggle**
    - **Validates: Requirements 5.2**

- [ ] 7. Make Dashboard the Default Entry Point

  - [ ] 7.1 Update main.py to launch dashboard by default
    - Import DashboardUI from dashboard.py
    - Replace InteractiveChatroom with DashboardUI in main()
    - Keep InteractiveChatroom available via --cli flag if needed
    - _Requirements: 3.1_

- [ ] 8. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
